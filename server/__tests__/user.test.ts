import request from 'supertest';
import express from 'express';
import session from 'express-session';
import userRoutes from '../routes/user.routes';
import { db } from '../db';

// Mock the database
jest.mock('../db', () => ({
  db: {
    select: jest.fn(),
    update: jest.fn(),
  },
  sql: jest.fn(),
}));

describe('User Routes', () => {
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
    
    app.use('/api/user', userRoutes);
    
    jest.clearAllMocks();
  });

  describe('GET /api/user/profile', () => {
    it('should return user profile', async () => {
      const mockUser = {
        id: 1,
        usn: '1SI20CS045',
        email: 'test@example.com',
        department: 'CSE',
        college: 'rvce',
        year: 1,
        notifyNewNotes: true,
        notifyDownloads: false
      };

      (db.select as jest.Mock).mockReturnValue({
        from: jest.fn().mockReturnThis(),
        where: jest.fn().mockResolvedValue([mockUser])
      });

      const response = await request(app)
        .get('/api/user/profile');

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('usn');
      expect(response.body).toHaveProperty('email');
      expect(response.body).not.toHaveProperty('password');
    });

    it('should require authentication', async () => {
      const unauthApp = express();
      unauthApp.use(express.json());
      unauthApp.use(session({
        secret: 'test-secret',
        resave: false,
        saveUninitialized: false
      }));
      unauthApp.use('/api/user', userRoutes);

      const response = await request(unauthApp)
        .get('/api/user/profile');

      expect(response.status).toBe(401);
    });
  });

  describe('PUT /api/user/settings', () => {
    it('should update notification settings', async () => {
      (db.update as jest.Mock).mockReturnValue({
        set: jest.fn().mockReturnThis(),
        where: jest.fn().mockResolvedValue({ rowCount: 1 })
      });

      const response = await request(app)
        .put('/api/user/settings')
        .send({
          notifyNewNotes: false,
          notifyDownloads: true
        });

      expect(response.status).toBe(200);
    });

    it('should validate settings fields', async () => {
      const response = await request(app)
        .put('/api/user/settings')
        .send({
          notifyNewNotes: 'invalid' // Should be boolean
        });

      expect(response.status).toBe(400);
    });
  });

  describe('PUT /api/user/password', () => {
    it('should validate password requirements', async () => {
      const response = await request(app)
        .put('/api/user/password')
        .send({
          currentPassword: 'OldPass@123',
          newPassword: 'weak',
          confirmNewPassword: 'weak'
        });

      expect(response.status).toBe(400);
      expect(response.body.error).toContain('at least 8 characters');
    });

    it('should require password confirmation match', async () => {
      const response = await request(app)
        .put('/api/user/password')
        .send({
          currentPassword: 'OldPass@123',
          newPassword: 'NewPass@123',
          confirmNewPassword: 'DifferentPass@123'
        });

      expect(response.status).toBe(400);
      expect(response.body.error).toContain('do not match');
    });
  });

  describe('GET /api/user/stats', () => {
    it('should return user statistics', async () => {
      // Mock user notes count
      (db.select as jest.Mock).mockReturnValueOnce({
        from: jest.fn().mockReturnThis(),
        where: jest.fn().mockResolvedValue([{ count: 5 }])
      });

      // Mock bookmarks count
      (db.select as jest.Mock).mockReturnValueOnce({
        from: jest.fn().mockReturnThis(),
        where: jest.fn().mockResolvedValue([{ count: 3 }])
      });

      const response = await request(app)
        .get('/api/user/stats');

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('notesUploaded');
      expect(response.body).toHaveProperty('bookmarksCount');
    });
  });
});
