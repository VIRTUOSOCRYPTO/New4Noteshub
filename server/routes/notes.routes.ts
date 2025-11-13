import { Router, Request, Response } from 'express';
import { storage } from '../storage';
import { searchNotesSchema, insertNoteSchema } from '@shared/schema';
import { ZodError } from 'zod';
import { fromZodError } from 'zod-validation-error';
import multer from 'multer';
import { v4 as uuidv4 } from 'uuid';
import path from 'path';
import fs from 'fs';
import { sanitizeUserText } from '../utils';
import { validateFile } from '../file-security';
import { logSecurityEvent, SecurityEventType, LogSeverity } from '../security-logger';

const router = Router();

// Set up multer for file storage
const uploadDir = path.join(process.cwd(), "uploads");

// Ensure upload directory exists
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

// Configure storage
const storage_ = multer.diskStorage({
  destination: function (req: Express.Request, file: Express.Multer.File, cb) {
    cb(null, uploadDir);
  },
  filename: function (req: Express.Request, file: Express.Multer.File, cb) {
    const extension = path.extname(file.originalname);
    const uniqueFilename = `${uuidv4()}${extension}`;
    cb(null, uniqueFilename);
  }
});

// Create multer upload middleware
const upload = multer({
  storage: storage_,
  limits: {
    fileSize: 15 * 1024 * 1024,
  },
  fileFilter: function (req: Express.Request, file: Express.Multer.File, cb) {
    const allowedMimeTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.ms-powerpoint',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      'text/plain',
      'text/markdown'
    ];
    
    if (allowedMimeTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only PDF, DOC, DOCX, PPT, PPTX, TXT, and MD files are allowed.'));
    }
  }
});

// Auth middleware (checks both session and JWT)
const isAuthenticated = async (req: Request, res: Response, next: Function) => {
  // First check for JWT token in headers
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
  
  // Fall back to session-based auth
  if (req.session && req.session.userId) {
    return next();
  }
  
  res.status(401).json({ error: 'Unauthorized' });
};

/**
 * GET /api/notes - Get notes with optional filters and pagination
 */
router.get('/', async (req: Request, res: Response) => {
  try {
    // Get user information if authenticated
    let userDepartment: string | undefined;
    let userCollege: string | undefined;
    let userYear: number | undefined;
    
    if (req.session.userId) {
      const user = await storage.getUser(req.session.userId);
      userDepartment = user?.department;
      userCollege = user?.college || undefined;
      userYear = user?.year;
    }
    
    // Check if we should show notes from all departments or not
    const showAllDepartments = req.query.showAllDepartments === 'true';
    const showAllColleges = req.query.showAllColleges === 'true';
    const showAllYears = req.query.showAllYears === 'true';
    
    // Parse pagination parameters
    const page = req.query.page ? parseInt(req.query.page as string) : 1;
    const limit = req.query.limit ? parseInt(req.query.limit as string) : 20;
    
    // Set up query parameters based on filter choices
    const queryParams = searchNotesSchema.parse({
      department: req.query.department as string | undefined,
      subject: req.query.subject as string | undefined,
      year: (req.query.year ? parseInt(req.query.year as string) : 0), 
      userDepartment: !showAllDepartments && !req.query.department ? userDepartment : undefined,
      userCollege: !showAllColleges ? userCollege : undefined,
      userYear: !showAllYears ? userYear : undefined,
      showAllDepartments: showAllDepartments,
      showAllColleges: showAllColleges,
      showAllYears: showAllYears || false,
      page,
      limit
    });
    
    // Use paginated query
    const { notes: notesData, total } = await storage.getNotesWithPagination(queryParams);
    
    // Calculate pagination metadata
    const totalPages = Math.ceil(total / limit);
    
    res.json({
      data: notesData,
      pagination: {
        page,
        limit,
        total,
        totalPages,
        hasNext: page < totalPages,
        hasPrev: page > 1
      }
    });
  } catch (error) {
    if (error instanceof ZodError) {
      const validationError = fromZodError(error);
      res.status(400).json({ error: validationError.message });
    } else {
      res.status(500).json({ error: 'Failed to fetch notes' });
    }
  }
});

/**
 * POST /api/notes - Upload a new note (requires authentication)
 */
router.post('/', isAuthenticated, upload.single('file'), async (req: Request<any, any, any, any> & { file?: Express.Multer.File }, res: Response) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const userId = req.session.userId!;
    const user = await storage.getUser(userId);
    
    if (!user) {
      return res.status(401).json({ error: 'User not found' });
    }
    
    // Enhanced file validation
    const fileValidation = await validateFile(req.file);
    if (!fileValidation.valid) {
      fs.unlinkSync(path.join(uploadDir, req.file.filename));
      return res.status(400).json({ error: fileValidation.message });
    }
    
    // Check for duplicate files
    const userDepartment = user.department;
    const existingNotes = await storage.getNotes({ department: userDepartment });
    
    const isDuplicate = existingNotes.some(note => {
      return note.originalFilename === req.file!.originalname && note.userId === userId;
    });
    
    if (isDuplicate) {
      fs.unlinkSync(path.join(uploadDir, req.file.filename));
      return res.status(409).json({ 
        error: 'Duplicate file detected',
        message: `A file with the name "${req.file.originalname}" has already been uploaded by you.`
      });
    }

    // Sanitize user input before validation
    const sanitizedTitle = sanitizeUserText(req.body.title);
    const sanitizedSubject = sanitizeUserText(req.body.subject);
    
    // Validate form data with sanitized inputs
    const noteData = insertNoteSchema.parse({
      usn: user.usn,
      title: sanitizedTitle,
      department: user.department,
      year: user.year || 1,
      subject: sanitizedSubject,
      filename: req.file.filename,
      originalFilename: req.file.originalname
    });
    
    // Log file uploads for security monitoring
    console.log(`[Security Log] File upload: User=${user.usn}, File=${req.file.originalname}, Type=${req.file.mimetype}, Size=${req.file.size}bytes`);
    
    // Store note metadata in storage
    const note = await storage.createNote(noteData, user.id);
    
    res.status(201).json(note);
  } catch (error) {
    // Clean up uploaded file if validation fails
    if (req.file) {
      fs.unlinkSync(path.join(uploadDir, req.file.filename));
    }
    
    if (error instanceof ZodError) {
      const validationError = fromZodError(error);
      res.status(400).json({ error: validationError.message });
    } else if (error instanceof Error) {
      res.status(400).json({ error: error.message });
    } else {
      res.status(500).json({ error: 'Failed to upload note' });
    }
  }
});

/**
 * GET /api/notes/:id/view - Increment view count for a note
 */
router.get('/:id/view', async (req: Request, res: Response) => {
  try {
    const noteId = parseInt(req.params.id);
    
    if (isNaN(noteId)) {
      return res.status(400).json({ error: 'Invalid note ID' });
    }
    
    await storage.incrementNoteViewCount(noteId);
    
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: 'Failed to track note view' });
  }
});

/**
 * GET /api/notes/:id/download - Download a note by ID
 */
router.get('/:id/download', async (req: Request, res: Response) => {
  try {
    const noteId = parseInt(req.params.id);
    const crypto = await import('crypto');
    
    if (isNaN(noteId)) {
      return res.status(400).json({ error: 'Invalid note ID' });
    }
    
    const note = await storage.getNoteById(noteId);
    
    if (!note) {
      return res.status(404).json({ error: 'Note not found' });
    }
    
    // Require login to download notes
    if (!req.session.userId) {
      logSecurityEvent(
        SecurityEventType.ACCESS_DENIED,
        LogSeverity.WARNING,
        req,
        `Unauthorized download attempt for note ID ${noteId}`
      );
      return res.status(401).json({ error: 'Please login to download notes' });
    }
    
    // Check if the user's academic year matches the note's year
    const user = await storage.getUser(req.session.userId);
    if (!user) {
      return res.status(401).json({ error: 'User not found' });
    }
    
    const showAllYears = req.query.showAllYears === 'true';
    if (!showAllYears && user.year !== note.year) {
      logSecurityEvent(
        SecurityEventType.ACCESS_DENIED,
        LogSeverity.WARNING,
        req,
        `Year mismatch on download attempt: User ${user.usn} (year ${user.year}) tried to download note ${noteId} (year ${note.year})`
      );
      return res.status(403).json({ 
        error: 'Access denied', 
        message: 'You can only download notes from your academic year'
      });
    }
    
    const filePath = path.join(uploadDir, note.filename);
    
    if (!fs.existsSync(filePath)) {
      return res.status(404).json({ error: 'File not found' });
    }
    
    // Increment the download count
    await storage.incrementNoteDownloadCount(noteId);
    
    // Sanitize filename
    const sanitizedFilename = note.originalFilename 
      ? note.originalFilename.replace(/[^\w\.\-]/g, '_')
      : `note_${noteId}${path.extname(note.filename)}`;
      
    // Determine content type
    const fileExtension = path.extname(note.filename).toLowerCase();
    let contentType = 'application/octet-stream';
    
    const contentTypeMap: Record<string, string> = {
      '.pdf': 'application/pdf',
      '.doc': 'application/msword',
      '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      '.ppt': 'application/vnd.ms-powerpoint',
      '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      '.txt': 'text/plain',
      '.md': 'text/markdown'
    };
    
    if (contentTypeMap[fileExtension]) {
      contentType = contentTypeMap[fileExtension];
    }
    
    // Calculate file hash for integrity
    const fileBuffer = fs.readFileSync(filePath);
    const fileHash = crypto.createHash('sha256').update(fileBuffer).digest('base64');
    
    // Set security headers
    res.setHeader('Content-Type', contentType);
    res.setHeader('Content-Disposition', `attachment; filename="${sanitizedFilename}"`);
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
    res.setHeader('Pragma', 'no-cache');
    res.setHeader('Expires', '0');
    res.setHeader('X-Content-Integrity', `sha256-${fileHash}`);
    
    // Log download
    logSecurityEvent(
      SecurityEventType.FILE_SECURITY,
      LogSeverity.INFO,
      req,
      `File download: User ${user.usn} downloaded note ${noteId} (${note.title})`
    );
    
    res.sendFile(filePath);
  } catch (error) {
    console.error('Download error:', error);
    res.status(500).json({ error: 'Failed to download note' });
  }
});

export default router;
