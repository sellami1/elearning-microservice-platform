const express = require("express");
const router = express.Router();
const {
  registerValidator,
  loginValidator,
  updateMeValidator,
} = require("../utils/validators/userValidator");

const {
  register,
  login,
  getMe,
  updateMe,
} = require("../controllers/userController");


const { protect } = require("../middleware/authMiddleware");
// const { authLimiter } = require("../utils/rateLimiter");

/**
 * @openapi
 * /api/v1/users/register:
 *   post:
 *     tags:
 *       - Users
 *     summary: Register a new user
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/RegisterRequest'
 *     responses:
 *       201:
 *         description: User registered successfully
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/RegistrationResponse'
 *       400:
 *         description: Validation error
 *       409:
 *         description: Email already in use
 */
router.post("/register", registerValidator, register);

/**
 * @openapi
 * /api/v1/users/login:
 *   post:
 *     tags:
 *       - Users
 *     summary: Login a user
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/LoginRequest'
 *     responses:
 *       200:
 *         description: Login successful
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/LoginResponse'
 *       401:
 *         description: Incorrect email or password
 */
router.post("/login", loginValidator, login);

/**
 * @openapi
 * /api/v1/users/me:
 *   get:
 *     tags:
 *       - Users
 *     summary: Get the authenticated user profile
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Authenticated user profile
 *       401:
 *         description: Missing or invalid token
 */
router.get("/me", protect, getMe);

/**
 * @openapi
 * /api/v1/users/update-me:
 *   put:
 *     tags:
 *       - Users
 *     summary: Update the authenticated user profile and address
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/UpdateMeRequest'
 *     responses:
 *       200:
 *         description: User profile updated successfully
 *       401:
 *         description: Missing or invalid token
 */
router.put("/update-me", protect, updateMeValidator, updateMe);

module.exports = router;
