import request from 'supertest';
import express from 'express';
import session from 'express-session';
import authRoutes from '../routes/auth.routes';

describe('Authentication Routes', () => {
  let app: express.Application;

  beforeEach(() => {
    // Create a fresh Express app for each test
    app = express();
    app.use(express.json());
    app.use(session({
      secret: 'test-secret',
      resave: false,
      saveUninitialized: false,
      cookie: { secure: false }
    }));
    app.use('/api/auth', authRoutes);
  });

  describe('POST /api/auth/register', () => {
    it('should reject registration with invalid USN format', async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send({
          usn: 'INVALID',
          email: 'test@example.com',
          department: 'CSE',
          college: 'rvce',
          year: 1,
          password: 'Test@1234',
          confirmPassword: 'Test@1234'
        });

      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('error');
    });

    it('should reject registration with weak password', async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send({
          usn: '1SI20CS045',
          email: 'test@example.com',
          department: 'CSE',
          college: 'rvce',
          year: 1,
          password: 'weak',
          confirmPassword: 'weak'
        });

      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('error');
    });

    it('should reject registration with mismatched passwords', async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send({
          usn: '1SI20CS045',
          email: 'test@example.com',
          department: 'CSE',
          college: 'rvce',
          year: 1,
          password: 'Test@1234',
          confirmPassword: 'Different@1234'
        });

      expect(response.status).toBe(400);
      expect(response.body.error).toContain('Passwords do not match');
    });
  });

  describe('POST /api/auth/login', () => {
    it('should reject login with invalid USN format', async () => {
      const response = await request(app)
        .post('/api/auth/login')
        .send({
          usn: 'INVALID',
          password: 'Test@1234'
        });

      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('error');
    });

    it('should return 401 for non-existent user', async () => {
      const response = await request(app)
        .post('/api/auth/login')
        .send({
          usn: '1SI20CS999',
          password: 'Test@1234'
        });

      expect(response.status).toBe(401);
      expect(response.body.error).toContain('not registered');
    });
  });

  describe('POST /api/auth/logout', () => {
    it('should successfully logout', async () => {
      const response = await request(app)
        .post('/api/auth/logout');

      expect(response.status).toBe(200);
      expect(response.body.message).toContain('Logged out successfully');
    });
  });

  describe('POST /api/auth/forgot-password', () => {
    it('should reject invalid email format', async () => {
      const response = await request(app)
        .post('/api/auth/forgot-password')
        .send({
          email: 'invalid-email'
        });

      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('error');
    });

    it('should accept valid email (security: dont reveal if exists)', async () => {
      const response = await request(app)
        .post('/api/auth/forgot-password')
        .send({
          email: 'test@example.com'
        });

      // Should return 200 regardless of whether email exists
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('message');
    });
  });

  describe('POST /api/auth/reset-password', () => {
    it('should reject invalid token', async () => {
      const response = await request(app)
        .post('/api/auth/reset-password')
        .send({
          token: 'invalid-token',
          newPassword: 'NewTest@1234',
          confirmPassword: 'NewTest@1234'
        });

      expect(response.status).toBe(400);
      expect(response.body.error).toContain('Invalid or expired token');
    });

    it('should reject weak new password', async () => {
      const response = await request(app)
        .post('/api/auth/reset-password')
        .send({
          token: 'some-token',
          newPassword: 'weak',
          confirmPassword: 'weak'
        });

      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('error');
    });
  });

  describe('POST /api/auth/google', () => {
    it('should reject missing email', async () => {
      const response = await request(app)
        .post('/api/auth/google')
        .send({
          idToken: 'fake-token'
        });

      expect(response.status).toBe(400);
      expect(response.body.error).toContain('Email is required');
    });
  });
});
