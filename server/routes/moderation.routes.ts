import { Router, Request, Response } from 'express';
import { storage } from '../storage';
import { sanitizeUserText } from '../utils';

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

/**
 * POST /api/moderation/notes/:id/flag - Flag a note as suspicious
 */
router.post('/notes/:id/flag', isAuthenticated, async (req: Request, res: Response) => {
  try {
    const noteId = parseInt(req.params.id);
    
    if (isNaN(noteId)) {
      return res.status(400).json({ error: 'Invalid note ID' });
    }
    
    const { reason } = req.body;
    if (!reason || typeof reason !== 'string' || reason.trim() === '') {
      return res.status(400).json({ error: 'Please provide a reason for flagging this content' });
    }
    
    const sanitizedReason = sanitizeUserText(reason);
    
    const note = await storage.getNoteById(noteId);
    if (!note) {
      return res.status(404).json({ error: 'Note not found' });
    }
    
    const userId = req.session.userId!;
    const user = await storage.getUser(userId);
    
    if (!user) {
      return res.status(401).json({ error: 'User not found' });
    }
    
    if (user.department !== note.department) {
      return res.status(403).json({ 
        error: 'Permission denied', 
        message: 'You can only flag notes from your own department'
      });
    }
    
    console.log(`[Security Log] Note flagged: ID=${noteId}, Flagger=${user.usn}, Reason=${sanitizedReason}`);
    
    const flaggedNote = await storage.flagNote(noteId, sanitizedReason);
    
    res.json({ 
      message: 'Note has been flagged for review',
      note: flaggedNote
    });
  } catch (error) {
    if (error instanceof Error) {
      res.status(400).json({ error: error.message });
    } else {
      res.status(500).json({ error: 'Failed to flag note' });
    }
  }
});

/**
 * GET /api/moderation/notes/flagged - Get all flagged notes
 */
router.get('/notes/flagged', isAuthenticated, async (req: Request, res: Response) => {
  try {
    const userId = req.session.userId!;
    const user = await storage.getUser(userId);
    
    if (!user) {
      return res.status(403).json({ error: 'You do not have permission to access this resource' });
    }
    
    const flaggedNotes = await storage.getFlaggedNotes();
    
    res.json(flaggedNotes);
  } catch (error) {
    if (error instanceof Error) {
      res.status(400).json({ error: error.message });
    } else {
      res.status(500).json({ error: 'Failed to get flagged notes' });
    }
  }
});

/**
 * POST /api/moderation/notes/:id/review - Review a flagged note
 */
router.post('/notes/:id/review', isAuthenticated, async (req: Request, res: Response) => {
  try {
    const noteId = parseInt(req.params.id);
    
    if (isNaN(noteId)) {
      return res.status(400).json({ error: 'Invalid note ID' });
    }
    
    const { approved } = req.body;
    if (typeof approved !== 'boolean') {
      return res.status(400).json({ error: 'Please specify whether the note is approved (true) or rejected (false)' });
    }
    
    const userId = req.session.userId!;
    const user = await storage.getUser(userId);
    
    if (!user) {
      return res.status(403).json({ error: 'You do not have permission to access this resource' });
    }
    
    const note = await storage.getNoteById(noteId);
    if (!note) {
      return res.status(404).json({ error: 'Note not found' });
    }
    
    if (!note.isFlagged) {
      return res.status(400).json({ error: 'This note is not flagged for review' });
    }
    
    console.log(`[Security Log] Note review: ID=${noteId}, Reviewer=${user.usn}, Decision=${approved ? 'Approved' : 'Rejected'}`);
    
    const reviewedNote = await storage.reviewFlaggedNote(noteId, approved);
    
    if (approved) {
      res.json({ 
        message: 'Note has been approved and is now available',
        note: reviewedNote
      });
    } else {
      res.json({ 
        message: 'Note has been rejected and removed from the system',
        note: reviewedNote
      });
    }
  } catch (error) {
    if (error instanceof Error) {
      res.status(400).json({ error: error.message });
    } else {
      res.status(500).json({ error: 'Failed to review note' });
    }
  }
});

export default router;
