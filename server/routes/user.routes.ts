import { Router, Request, Response } from 'express';
import { storage } from '../storage';
import { updateUserSettingsSchema, updatePasswordSchema } from '@shared/schema';
import { ZodError } from 'zod';
import { fromZodError } from 'zod-validation-error';
import multer from 'multer';
import { v4 as uuidv4 } from 'uuid';
import path from 'path';
import fs from 'fs';

const router = Router();

// Auth middleware
const isAuthenticated = async (req: Request, res: Response, next: Function) => {
  const authHeader = req.headers.authorization;
  if (authHeader && authHeader.startsWith('Bearer ')) {
    const token = authHeader.substring(7);
    try {
      const { verifyToken } = await import('../jwt');
      const decoded = verifyToken(token);
      if (decoded && decoded.userId) {
        req.session.userId = decoded.userId;
        return next();
      }
    } catch (error) {
      console.error('Token verification failed:', error);
    }
  }
  
  if (req.session && req.session.userId) {
    return next();
  }
  
  res.status(401).json({ error: 'Unauthorized' });
};

// Configure profile picture upload
const profilePicStorage = multer.diskStorage({
  destination: function (req: Express.Request, file: Express.Multer.File, cb) {
    const profileDir = path.join(process.cwd(), "uploads/profile");
    if (!fs.existsSync(profileDir)) {
      fs.mkdirSync(profileDir, { recursive: true });
    }
    cb(null, profileDir);
  },
  filename: function (req: Express.Request, file: Express.Multer.File, cb) {
    const extension = path.extname(file.originalname);
    const uniqueFilename = `profile_${uuidv4()}${extension}`;
    cb(null, uniqueFilename);
  }
});

const profileUpload = multer({
  storage: profilePicStorage,
  limits: {
    fileSize: 5 * 1024 * 1024, // 5MB
  },
  fileFilter: function (req: Express.Request, file: Express.Multer.File, cb) {
    const allowedMimeTypes = [
      'image/jpeg',
      'image/png',
      'image/gif',
      'image/webp'
    ];
    
    if (allowedMimeTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only JPG, PNG, GIF and WebP images are allowed.'));
    }
  }
});

/**
 * GET /api/user - Get current user info
 */
router.get('/', isAuthenticated, async (req: Request, res: Response) => {
  try {
    if (!req.session.userId) {
      return res.status(401).json({ error: 'Not authenticated' });
    }
    
    const userId = req.session.userId;
    const user = await storage.getUser(userId);
    
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    const { password, ...userWithoutPassword } = user;
    res.json(userWithoutPassword);
  } catch (error) {
    res.status(500).json({ error: 'Failed to get user data' });
  }
});

/**
 * PATCH /api/user/settings - Update user settings
 */
router.patch('/settings', isAuthenticated, async (req: Request, res: Response) => {
  try {
    if (!req.session.userId) {
      return res.status(401).json({ error: 'Not authenticated' });
    }
    
    const settingsData = updateUserSettingsSchema.parse(req.body);
    const updatedUser = await storage.updateUserSettings(req.session.userId, settingsData);
    
    const { password, ...userWithoutPassword } = updatedUser;
    res.json(userWithoutPassword);
  } catch (error) {
    if (error instanceof ZodError) {
      const validationError = fromZodError(error);
      res.status(400).json({ error: validationError.message });
    } else if (error instanceof Error) {
      res.status(400).json({ error: error.message });
    } else {
      res.status(500).json({ error: 'Failed to update settings' });
    }
  }
});

/**
 * PATCH /api/user/password - Update user password
 */
router.patch('/password', isAuthenticated, async (req: Request, res: Response) => {
  try {
    if (!req.session.userId) {
      return res.status(401).json({ error: 'Not authenticated' });
    }
    
    const passwordData = updatePasswordSchema.parse(req.body);
    
    await storage.updatePassword(
      req.session.userId,
      passwordData.currentPassword,
      passwordData.newPassword
    );
    
    res.json({ message: 'Password updated successfully' });
  } catch (error) {
    if (error instanceof ZodError) {
      const validationError = fromZodError(error);
      res.status(400).json({ error: validationError.message });
    } else if (error instanceof Error) {
      res.status(400).json({ error: error.message });
    } else {
      res.status(500).json({ error: 'Failed to update password' });
    }
  }
});

/**
 * POST /api/user/profile-picture - Upload profile picture
 */
router.post('/profile-picture', isAuthenticated, profileUpload.single('profilePicture'), async (req: Request<any, any, any, any> & { file?: Express.Multer.File }, res: Response) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }
    
    if (!req.session.userId) {
      return res.status(401).json({ error: 'Not authenticated' });
    }
    
    const updatedUser = await storage.updateProfilePicture(
      req.session.userId,
      req.file.filename
    );
    
    const { password, ...userWithoutPassword } = updatedUser;
    res.json(userWithoutPassword);
  } catch (error) {
    if (req.file) {
      fs.unlinkSync(path.join(process.cwd(), 'uploads/profile', req.file.filename));
    }
    
    if (error instanceof Error) {
      res.status(400).json({ error: error.message });
    } else {
      res.status(500).json({ error: 'Failed to upload profile picture' });
    }
  }
});

/**
 * GET /api/user/profile-picture/:filename - Get profile picture
 */
router.get('/profile-picture/:filename', async (req: Request, res: Response) => {
  try {
    const filename = req.params.filename;
    
    // Validate filename format
    if (!filename.match(/^profile_[a-f0-9\-]{36}\.(jpg|jpeg|png|gif|webp)$/i)) {
      return res.status(400).json({ error: 'Invalid filename format' });
    }
    
    const filePath = path.join(process.cwd(), 'uploads/profile', filename);
    
    if (!fs.existsSync(filePath)) {
      return res.status(404).json({ error: 'Profile picture not found' });
    }
    
    const fileExtension = path.extname(filename).toLowerCase();
    let contentType = 'application/octet-stream';
    
    const contentTypeMap: Record<string, string> = {
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
      '.png': 'image/png',
      '.gif': 'image/gif',
      '.webp': 'image/webp'
    };
    
    if (contentTypeMap[fileExtension]) {
      contentType = contentTypeMap[fileExtension];
    }
    
    res.setHeader('Content-Type', contentType);
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('Content-Security-Policy', "default-src 'self'");
    res.setHeader('Cache-Control', 'max-age=86400');
    
    res.sendFile(filePath);
  } catch (error) {
    console.error('Profile picture error:', error);
    res.status(500).json({ error: 'Failed to get profile picture' });
  }
});

/**
 * GET /api/user/stats - Get user stats for achievements
 */
router.get('/stats', isAuthenticated, async (req: Request, res: Response) => {
  try {
    const userId = req.session.userId as number;
    
    const user = await storage.getUser(userId);
    if (!user) {
      return res.status(404).json({ error: "User not found" });
    }
    
    const userNotes = await storage.getNotes({ userId: userId });
    
    const daysSinceJoined = Math.floor(
      (Date.now() - new Date(user.createdAt).getTime()) / (1000 * 60 * 60 * 24)
    );
    
    // Mock data for demo (in production, these would be tracked)
    const viewCount = Math.floor(Math.random() * 30);
    const downloadCount = Math.floor(Math.random() * 15);
    const previewCount = Math.floor(Math.random() * 40);
    const uniqueSubjectsCount = Math.floor(Math.random() * 10);
    const pagesVisited = Math.floor(Math.random() * 6);
    
    const stats = {
      uploadCount: userNotes.length,
      downloadCount,
      viewCount,
      daysSinceJoined,
      previewCount,
      uniqueSubjectsCount,
      pagesVisited
    };
    
    console.log(`User stats for ${user.usn}:`, stats);
    
    return res.json(stats);
  } catch (error) {
    console.error("Error getting user stats:", error);
    return res.status(500).json({ error: "Failed to get user stats" });
  }
});

export default router;
