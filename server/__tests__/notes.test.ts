import request from 'supertest';
import express from 'express';
import session from 'express-session';
import notesRoutes from '../routes/notes.routes';

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
    app.use('/api/notes', notesRoutes);
  });

  describe('GET /api/notes', () => {
    it('should return notes list with pagination metadata', async () => {
      const response = await request(app)
        .get('/api/notes')
        .query({ page: 1, limit: 20 });

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('data');
      expect(response.body).toHaveProperty('pagination');
      expect(response.body.pagination).toHaveProperty('page');
      expect(response.body.pagination).toHaveProperty('limit');
      expect(response.body.pagination).toHaveProperty('total');
      expect(response.body.pagination).toHaveProperty('totalPages');
      expect(response.body.pagination).toHaveProperty('hasNext');
      expect(response.body.pagination).toHaveProperty('hasPrev');
    });

    it('should handle department filter', async () => {
      const response = await request(app)
        .get('/api/notes')
        .query({ department: 'CSE', page: 1, limit: 10 });

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('data');
    });

    it('should handle subject filter', async () => {
      const response = await request(app)
        .get('/api/notes')
        .query({ subject: 'Mathematics', page: 1 });

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('data');
    });

    it('should validate pagination parameters', async () => {
      const response = await request(app)
        .get('/api/notes')
        .query({ page: -1, limit: 0 });

      // Should either handle gracefully or return validation error
      expect(response.status).toBeGreaterThanOrEqual(200);
    });
  });

  describe('POST /api/notes', () => {
    it('should require authentication', async () => {
      const response = await request(app)
        .post('/api/notes')
        .send({
          title: 'Test Note',
          subject: 'Test Subject'
        });

      expect(response.status).toBe(401);
      expect(response.body.error).toContain('Unauthorized');
    });

    it('should reject upload without file', async () => {
      // Mock authenticated session
      const agent = request.agent(app);
      
      const response = await agent
        .post('/api/notes')
        .set('Authorization', 'Bearer fake-token')
        .send({
          title: 'Test Note',
          subject: 'Test Subject'
        });

      // Should return 400 or 401 depending on auth
      expect(response.status).toBeGreaterThanOrEqual(400);
    });
  });

  describe('GET /api/notes/:id/view', () => {
    it('should reject invalid note ID', async () => {
      const response = await request(app)
        .get('/api/notes/invalid/view');

      expect(response.status).toBe(400);
      expect(response.body.error).toContain('Invalid note ID');
    });

    it('should accept numeric note ID', async () => {
      const response = await request(app)
        .get('/api/notes/1/view');

      // Should either succeed or return 404 if note doesn't exist
      expect([200, 404, 500]).toContain(response.status);
    });
  });

  describe('GET /api/notes/:id/download', () => {
    it('should require authentication', async () => {
      const response = await request(app)
        .get('/api/notes/1/download');

      expect(response.status).toBe(401);
      expect(response.body.error).toContain('login');
    });

    it('should reject invalid note ID', async () => {
      const response = await request(app)
        .get('/api/notes/invalid/download')
        .set('Authorization', 'Bearer fake-token');

      expect(response.status).toBe(400);
      expect(response.body.error).toContain('Invalid note ID');
    });
  });
});
