import { Router, Request, Response } from 'express';
import { storage } from '../storage';
import { 
  registerUserSchema, 
  loginUserSchema,
  forgotPasswordSchema,
  resetPasswordSchema,
  googleAuthSchema,
  type User 
} from '@shared/schema';
import { ZodError } from 'zod';
import { fromZodError } from 'zod-validation-error';
import { generateAccessToken, generateRefreshToken } from '../jwt';
import { logSecurityEvent, SecurityEventType, LogSeverity } from '../security-logger';

const router = Router();

/**
 * POST /api/auth/register - Register a new user
 */
router.post('/register', async (req: Request, res: Response) => {
  try {
    // First, manually validate the USN and department code match
    if (req.body.usn && req.body.department) {
      const usn = req.body.usn.toUpperCase();
      const department = req.body.department;
      
      // Extract department code using regex pattern
      const usnPattern = /^[0-9][A-Za-z]{2}[0-9]{2}([A-Za-z]{2})[0-9]{3}$/;
      const match = usn.match(usnPattern);
      
      if (match) {
        // The department code is in the first capture group
        const usnDeptCode = match[1];
        
        // Import DEPARTMENT_CODES from schema
        const { DEPARTMENT_CODES } = await import('@shared/schema');
        
        // Check if department code maps to expected department
        const expectedDept = DEPARTMENT_CODES[usnDeptCode];
        
        if (expectedDept && expectedDept !== department) {
          return res.status(400).json({
            error: `USN department code '${usnDeptCode}' doesn't match selected department '${department}'. Expected: '${expectedDept}'`
          });
        }
      }
    }
    
    // Proceed with standard validation
    const userData = registerUserSchema.parse(req.body);
    
    // First check if user with this USN already exists before registration
    const existingUser = await storage.getUserByUSN(userData.usn);
    if (existingUser) {
      return res.status(409).json({ error: "USN already exists. Please login instead." });
    }
    
    // Year validation is no longer needed, but we'll keep default for backward compatibility
    userData.year = userData.year || 1; // Default to 1 if not provided

    // Register the user
    const user = await storage.registerUser({
      usn: userData.usn,
      email: userData.email,
      department: userData.department,
      college: userData.college,
      year: userData.year,
      password: userData.password
    });
    
    // Set session
    req.session.userId = user.id;
    
    // Return user data (excluding password)
    const { password, ...userWithoutPassword } = user;
    res.status(201).json(userWithoutPassword);
  } catch (error) {
    if (error instanceof ZodError) {
      const validationError = fromZodError(error);
      res.status(400).json({ error: validationError.message });
    } else if (error instanceof Error) {
      // Check for specific error messages
      if (error.message.includes("already registered") || error.message.includes("already exists")) {
        res.status(409).json({ error: "USN already exists. Please login instead." });
      } else {
        res.status(400).json({ error: error.message });
      }
    } else {
      res.status(500).json({ error: 'Failed to register user' });
    }
  }
});

/**
 * POST /api/auth/login - User login
 */
router.post('/login', async (req: Request, res: Response) => {
  try {
    // Validate login data
    const loginData = loginUserSchema.parse(req.body);
    
    // First check if the USN exists
    const userExists = await storage.getUserByUSN(loginData.usn);
    if (!userExists) {
      return res.status(401).json({ error: 'USN not registered. Please register first.' });
    }
    
    // Authenticate user
    const user = await storage.validateLogin(loginData);
    
    if (!user) {
      return res.status(401).json({ error: 'Incorrect password. Please try again.' });
    }
    
    // Check if 2FA is enabled for this user
    const twoFactorEnabled = await storage.isTwoFactorEnabled(user.id);
    
    if (twoFactorEnabled) {
      // Store temporary user ID for 2FA verification
      req.session.tempUserId = user.id;
      
      // Return 2FA required status
      return res.status(200).json({
        twoFactorRequired: true,
        message: 'Two-factor authentication required'
      });
    }
    
    // Standard login (no 2FA)
    // Set session
    req.session.userId = user.id;
    
    // Generate JWT tokens
    const accessToken = generateAccessToken(user);
    const refreshToken = generateRefreshToken(user);
    
    // Store refresh token
    await storage.storeRefreshToken(user.id, refreshToken);
    
    // Return user data with tokens
    const { password, ...userWithoutPassword } = user;
    res.json({
      user: userWithoutPassword,
      accessToken,
      refreshToken
    });
  } catch (error) {
    if (error instanceof ZodError) {
      const validationError = fromZodError(error);
      res.status(400).json({ error: validationError.message });
    } else if (error instanceof Error) {
      res.status(500).json({ error: error.message });
    } else {
      res.status(500).json({ error: 'Failed to login' });
    }
  }
});

/**
 * POST /api/auth/logout - User logout
 */
router.post('/logout', (req: Request, res: Response) => {
  req.session.destroy((err) => {
    if (err) {
      return res.status(500).json({ error: 'Failed to logout' });
    }
    // Clear the cookie with the same settings as when it was set
    res.clearCookie('connect.sid', {
      path: '/',
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: process.env.NODE_ENV === "production" ? 'none' : 'lax',
      domain: undefined
    });
    res.status(200).json({ message: 'Logged out successfully' });
  });
});

/**
 * POST /api/auth/google - Google Authentication
 */
router.post('/google', async (req: Request, res: Response) => {
  try {
    // Validate Google auth data
    const googleData = googleAuthSchema.parse(req.body);
    
    if (!googleData.email) {
      return res.status(400).json({ error: 'Email is required for Google authentication' });
    }
    
    // Check if the user with this email already exists in our system
    const user = await storage.authenticateWithGoogle(googleData.email);
    
    if (user) {
      // Whether existing or new user, complete the authentication process
      req.session.userId = user.id;
      
      // Prepare and return safe user data
      const { password, ...safeUser } = user;
      
      // Generate JWT tokens
      const accessToken = generateAccessToken(user);
      const refreshToken = generateRefreshToken(user);
      
      // Store refresh token in the database
      await storage.storeRefreshToken(user.id, refreshToken);
      
      // Determine if this is a newly created user
      const isNewUser = user.createdAt && 
        (new Date().getTime() - new Date(user.createdAt).getTime()) < 5000;
      
      return res.status(200).json({
        user: safeUser,
        accessToken,
        refreshToken,
        isNewUser
      });
    } else {
      return res.status(500).json({ 
        error: 'Unable to authenticate with Google. Please try again.'
      });
    }
  } catch (error) {
    if (error instanceof ZodError) {
      const validationError = fromZodError(error);
      return res.status(400).json({ error: validationError.message });
    }
    console.error('Google auth error:', error);
    return res.status(500).json({ 
      error: error instanceof Error ? error.message : 'Failed to authenticate with Google'
    });
  }
});

/**
 * POST /api/auth/forgot-password - Initiate password reset
 */
router.post('/forgot-password', async (req: Request, res: Response) => {
  try {
    // Validate request data
    const { email } = forgotPasswordSchema.parse(req.body);
    
    // Create reset token in database
    const token = await storage.createPasswordResetToken(email);
    
    if (!token) {
      // Don't reveal if email exists in DB for security reasons
      return res.json({ 
        message: "If a matching account was found, a password reset link has been sent."
      });
    }
    
    // In a real application, you would send an email with reset token here
    const resetLink = `${req.protocol}://${req.get('host')}/reset-password?token=${token}`;
    
    console.log(`Password reset link for ${email}: ${resetLink}`);
    
    return res.json({ 
      message: "Password reset email sent",
      resetLink 
    });
  } catch (error) {
    if (error instanceof ZodError) {
      const validationError = fromZodError(error);
      res.status(400).json({ error: validationError.message });
    } else if (error instanceof Error) {
      res.status(500).json({ error: error.message });
    } else {
      res.status(500).json({ error: 'Failed to process request' });
    }
  }
});

/**
 * POST /api/auth/reset-password - Complete password reset
 */
router.post('/reset-password', async (req: Request, res: Response) => {
  try {
    // Validate request data
    const { token, newPassword } = resetPasswordSchema.parse(req.body);
    
    // Reset password in database
    const success = await storage.resetPassword(token, newPassword);
    
    if (!success) {
      return res.status(400).json({ error: "Invalid or expired token" });
    }
    
    return res.json({ message: "Password has been reset successfully" });
  } catch (error) {
    if (error instanceof ZodError) {
      const validationError = fromZodError(error);
      res.status(400).json({ error: validationError.message });
    } else if (error instanceof Error) {
      res.status(500).json({ error: error.message });
    } else {
      res.status(500).json({ error: 'Failed to reset password' });
    }
  }
});

export default router;
