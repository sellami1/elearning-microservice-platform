const rateLimit = require('express-rate-limit');
const ApiError = require('./apiError');

/**
 * @desc    Global Limiter for all API routes
 * @limit   100 requests per 15 minutes
 */
exports.globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, 
  handler: (req, res, next) => {
    next(new ApiError('Too many requests from this IP, please try again after 15 minutes', 429));
  },
  standardHeaders: true,
  legacyHeaders: false,
});

/**
 * @desc    Strict Limiter for Auth routes (Login/Register)
 * @limit   10 requests per 15 minutes
 */
exports.authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,
  handler: (req, res, next) => {
    next(new ApiError('Too many authentication attempts. Please try again later', 429));
  },
  standardHeaders: true,
  legacyHeaders: false,
});

/**
 * @desc    Very Strict Limiter for Email/Reset actions
 * @limit   3 requests per hour
 */
exports.forgotPasswordLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 3,
  handler: (req, res, next) => {
    next(new ApiError('Too many reset/verification requests. Please try again in an hour', 429));
  },
  standardHeaders: true,
  legacyHeaders: false,
});
