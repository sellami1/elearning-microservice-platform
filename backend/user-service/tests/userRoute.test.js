const request = require('supertest');
const express = require('express');
const User = require('../src/models/userModel');
const Email = require('../src/utils/emailTemplate');
const { hashToken } = require('../src/utils/verificationToken');
const createToken = require('../src/utils/createJWT');
const crypto = require('crypto');

// Set environment variables for testing
process.env.JWT_SECRET_KEY = 'test_secret_key';
process.env.JWT_EXPIRE_TIME = '1h';
process.env.PUBLIC_FRONTEND_URL = 'http://localhost:3000';

// Mock Email module
jest.mock('../src/utils/emailTemplate', () => ({
  verifyEmail: jest.fn().mockResolvedValue(true),
  forgotPassword: jest.fn().mockResolvedValue(true),
  passwordChanged: jest.fn().mockResolvedValue(true),
  newLoginDetected: jest.fn().mockResolvedValue(true),
  sendEmailUpdateLink: jest.fn().mockResolvedValue(true),
  notifyEmailChanged: jest.fn().mockResolvedValue(true),
}));

// Mock rate limiters
jest.mock('../src/utils/rateLimiter', () => ({
  globalLimiter: (req, res, next) => next(),
  authLimiter: (req, res, next) => next(),
  forgotPasswordLimiter: (req, res, next) => next(),
}));

// Mock User model
jest.mock('../src/models/userModel');

// Setup app
const app = express();
app.use(express.json());
require('../src/routes')(app);

// Simple error handler for tests
app.use((err, req, res, next) => {
  res.status(err.statusCode || 500).json({
    status: err.status || 'error',
    message: err.message,
    errors: err.errors
  });
});

const validPassword = 'Password123!';
const validToken = crypto.randomBytes(32).toString('hex');

const userData = {
  email: 'test@example.com',
  password: validPassword,
  passwordConfirm: validPassword,
  firstName: 'John',
  lastName: 'Doe',
  phone: '+12125550123',
  role: 'learner',
  dateOfBirth: '1990-01-01',
  street: 'Main Street',
  city: 'New York',
  state: 'NY',
  country: 'US',
  zipCode: '10001'
};

const createMockUser = () => ({
  _id: '507f1f77bcf86cd799439011',
  email: userData.email,
  role: userData.role,
  isVerified: true,
  profile: { firstName: userData.firstName, lastName: userData.lastName },
  address: { country: 'US' },
  comparePassword: jest.fn().mockResolvedValue(true),
  save: jest.fn().mockImplementation(function() { return Promise.resolve(this); }),
});

describe('User Service - 17 Detailed Tests', () => {
  let mockUser;

  const setupMockQuery = (targetUser) => ({
    select: jest.fn().mockReturnThis(),
    exec: jest.fn().mockResolvedValue(targetUser),
    then: jest.fn().mockImplementation(function(cb) { return Promise.resolve(targetUser).then(cb); }),
    catch: jest.fn().mockReturnThis()
  });

  beforeEach(() => {
    jest.clearAllMocks();
    mockUser = createMockUser();
    const defaultQuery = setupMockQuery(mockUser);
    User.findOne.mockReturnValue(defaultQuery);
    User.findById.mockReturnValue(defaultQuery);
    User.create.mockResolvedValue(mockUser);
  });

  describe('Registration & Basic Auth', () => {
    it('1. SUCCESS: Register', async () => {
      User.findOne.mockReturnValueOnce(setupMockQuery(null));
      const res = await request(app).post('/api/v1/users/register').send(userData);
      expect(res.statusCode).toBe(201);
    });

    it('2. ERROR: Register (Missing Fields)', async () => {
      const res = await request(app).post('/api/v1/users/register').send({ email: 'test@example.com' });
      expect(res.statusCode).toBe(400);
    });

    it('3. ERROR: Register (Duplicate Email)', async () => {
      User.findOne.mockReturnValueOnce(setupMockQuery(mockUser));
      const res = await request(app).post('/api/v1/users/register').send(userData);
      expect(res.statusCode).toBe(400);
      expect(res.body.errors[0].msg).toContain('already in use');
    });

    it('4. SUCCESS: Login', async () => {
      const res = await request(app).post('/api/v1/users/login').send({
        email: userData.email, password: userData.password, role: userData.role
      });
      expect(res.statusCode).toBe(200);
      expect(res.body.token).toBeDefined();
    });

    it('5. ERROR: Login (Wrong Password)', async () => {
      mockUser.comparePassword.mockResolvedValueOnce(false);
      const res = await request(app).post('/api/v1/users/login').send({
        email: userData.email, password: 'wrongpassword', role: userData.role
      });
      expect(res.statusCode).toBe(401);
    });

    it('6. ERROR: Login (Unverified)', async () => {
      mockUser.isVerified = false;
      const res = await request(app).post('/api/v1/users/login').send({
        email: userData.email, password: userData.password, role: userData.role
      });
      expect(res.statusCode).toBe(401);
    });
  });

  describe('Email Flow', () => {
    it('7. SUCCESS: Verify Email', async () => {
      mockUser.isVerified = false;
      const res = await request(app).put(`/api/v1/users/verify-email/${validToken}`);
      expect(res.statusCode).toBe(200);
      expect(mockUser.isVerified).toBe(true);
    });

    it('8. ERROR: Verify Email (Invalid Token Format)', async () => {
      const res = await request(app).put('/api/v1/users/verify-email/short');
      expect(res.statusCode).toBe(400);
    });

    it('9. SUCCESS: Resend Verification', async () => {
      mockUser.isVerified = false;
      const res = await request(app).post('/api/v1/users/resend-verification-email').send({ email: userData.email });
      expect(res.statusCode).toBe(200);
    });

    it('10. SUCCESS: Request Email Update', async () => {
      const token = createToken({ id: mockUser._id, role: mockUser.role });
      User.findOne.mockReturnValueOnce(setupMockQuery(null));
      const res = await request(app).post('/api/v1/users/request-email-update')
        .set('Authorization', `Bearer ${token}`)
        .send({ newEmail: 'new@example.com', currentPassword: validPassword });
      expect(res.statusCode).toBe(200);
    });

    it('11. SUCCESS: Verify Email Update', async () => {
      const token = createToken({ id: mockUser._id, role: mockUser.role });
      const res = await request(app).put(`/api/v1/users/verify-email-update/${validToken}`)
        .set('Authorization', `Bearer ${token}`);
      expect(res.statusCode).toBe(200);
    });
  });

  describe('Password Flow', () => {
    it('12. SUCCESS: Forgot Password', async () => {
      const res = await request(app).post('/api/v1/users/forgotPassword').send({ email: userData.email });
      expect(res.statusCode).toBe(200);
    });

    it('13. SUCCESS: Reset Password', async () => {
      const res = await request(app).put(`/api/v1/users/resetPassword/${validToken}`).send({
        password: 'NewStrongPassword1!', passwordConfirm: 'NewStrongPassword1!'
      });
      expect(res.statusCode).toBe(200);
    });

    it('14. SUCCESS: Update My Password', async () => {
      const token = createToken({ id: mockUser._id, role: mockUser.role });
      const res = await request(app).put('/api/v1/users/update-my-password')
        .set('Authorization', `Bearer ${token}`)
        .send({
          currentPassword: validPassword,
          password: 'NewInAppPassword1!',
          passwordConfirm: 'NewInAppPassword1!'
        });
      expect(res.statusCode).toBe(200);
    });
  });

  describe('Profile Access', () => {
    let token;
    beforeEach(() => { token = createToken({ id: mockUser._id, role: mockUser.role }); });

    it('15. SUCCESS: Get Me', async () => {
      const res = await request(app).get('/api/v1/users/me').set('Authorization', `Bearer ${token}`);
      expect(res.statusCode).toBe(200);
      expect(res.body.data.email).toBe(userData.email);
    });

    it('16. SUCCESS: Update Me', async () => {
      const res = await request(app).put('/api/v1/users/update-me').set('Authorization', `Bearer ${token}`).send({ firstName: 'Jane' });
      expect(res.statusCode).toBe(200);
    });

    it('17. ERROR: Unauthorized Access', async () => {
      const res = await request(app).get('/api/v1/users/me');
      expect(res.statusCode).toBe(401);
    });
  });
});
