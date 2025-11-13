import request from 'supertest';
import express from 'express';
import session from 'express-session';
import notesRoutes from '../routes/notes.routes';
import { db } from '../db';

// Mock the database
jest.mock('../db', () => ({
  db: {
    select: jest.fn(),
    insert: jest.fn(),
    update: jest.fn(),
    delete: jest.fn(),
  },
  sql: jest.fn(),
}));

describe('Notes Routes', () => {
  let app: express.Application;

  beforeEach(() => {
    app = express();
    app.use(express.json());
    app.use(session({
      secret: 'test-secret',
      resave: false,
      saveUninitialized: false,
      cookie: { secure: false }
    }));
    
    // Mock authenticated user
    app.use((req: any, res, next) => {
      req.session.userId = 1;
      req.session.usn = '1SI20CS045';
      next();
    });
    
    app.use('/api/notes', notesRoutes);
    
    jest.clearAllMocks();
  });

  describe('GET /api/notes', () => {
    it('should return paginated notes', async () => {
      const mockNotes = [
        {
          id: 1,
          title: 'Test Note 1',
          department: 'CSE',
          year: 1,
          subject: 'Data Structures',
          usn: '1SI20CS045'
        },
        {
          id: 2,
          title: 'Test Note 2',
          department: 'CSE',
          year: 1,
          subject: 'Algorithms',
          usn: '1SI20CS045'
        }
      ];

      // Mock successful response
      (db.select as jest.Mock).mockReturnValue({
        from: jest.fn().mockReturnThis(),
        where: jest.fn().mockReturnThis(),
        limit: jest.fn().mockReturnThis(),
        offset: jest.fn().mockResolvedValue(mockNotes)
      });

      const response = await request(app)
        .get('/api/notes')
        .query({ page: 1, limit: 20 });

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('data');
      expect(response.body).toHaveProperty('pagination');
    });

    it('should handle pagination parameters', async () => {
      const response = await request(app)
        .get('/api/notes')
        .query({ page: 2, limit: 10 });

      expect(response.status).toBe(200);
    });

    it('should filter by department', async () => {
      const response = await request(app)
        .get('/api/notes')
        .query({ department: 'CSE' });

      expect(response.status).toBe(200);
    });

    it('should filter by year', async () => {
      const response = await request(app)
        .get('/api/notes')
        .query({ year: 1 });

      expect(response.status).toBe(200);
    });
  });

  describe('POST /api/notes', () => {
    it('should reject upload without authentication', async () => {
      // Create app without auth middleware
      const unauthApp = express();
      unauthApp.use(express.json());
      unauthApp.use(session({
        secret: 'test-secret',
        resave: false,
        saveUninitialized: false
      }));
      unauthApp.use('/api/notes', notesRoutes);

      const response = await request(unauthApp)
        .post('/api/notes')
        .send({
          title: 'Test Note',
          department: 'CSE',
          year: 1,
          subject: 'Test Subject'
        });

      expect(response.status).toBe(401);
    });

    it('should validate required fields', async () => {
      const response = await request(app)
        .post('/api/notes')
        .send({
          title: 'Test Note'
          // Missing required fields
        });

      expect(response.status).toBe(400);
    });
  });

  describe('GET /api/notes/:id', () => {
    it('should return a single note by ID', async () => {
      const mockNote = {
        id: 1,
        title: 'Test Note',
        department: 'CSE',
        year: 1,
        subject: 'Data Structures',
        usn: '1SI20CS045'
      };

      (db.select as jest.Mock).mockReturnValue({
        from: jest.fn().mockReturnThis(),
        where: jest.fn().mockResolvedValue([mockNote])
      });

      const response = await request(app)
        .get('/api/notes/1');

      expect(response.status).toBe(200);
    });

    it('should return 404 for non-existent note', async () => {
      (db.select as jest.Mock).mockReturnValue({
        from: jest.fn().mockReturnThis(),
        where: jest.fn().mockResolvedValue([])
      });

      const response = await request(app)
        .get('/api/notes/999');

      expect(response.status).toBe(404);
    });
  });

  describe('DELETE /api/notes/:id', () => {
    it('should allow user to delete own note', async () => {
      const mockNote = {
        id: 1,
        userId: 1,
        title: 'Test Note',
        usn: '1SI20CS045'
      };

      (db.select as jest.Mock).mockReturnValue({
        from: jest.fn().mockReturnThis(),
        where: jest.fn().mockResolvedValue([mockNote])
      });

      (db.delete as jest.Mock).mockReturnValue({
        from: jest.fn().mockReturnThis(),
        where: jest.fn().mockResolvedValue({ rowCount: 1 })
      });

      const response = await request(app)
        .delete('/api/notes/1');

      expect(response.status).toBe(200);
    });

    it('should prevent user from deleting others note', async () => {
      const mockNote = {
        id: 1,
        userId: 999, // Different user
        title: 'Test Note',
        usn: '1SI20CS999'
      };

      (db.select as jest.Mock).mockReturnValue({
        from: jest.fn().mockReturnThis(),
        where: jest.fn().mockResolvedValue([mockNote])
      });

      const response = await request(app)
        .delete('/api/notes/1');

      expect(response.status).toBe(403);
    });
  });
});
