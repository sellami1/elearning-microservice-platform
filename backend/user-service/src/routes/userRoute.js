const express = require("express");
const router = express.Router();
const {
  registerValidator,
  verifyEmailValidator,
  resendVerificationValidator,
  loginValidator,
  forgotPasswordValidator,
  resetPasswordValidator,
  updateMeValidator,
  requestEmailUpdateValidator,
  verifyEmailUpdateValidator,
  updatePasswordValidator,
} = require("../utils/validators/userValidator");

const {
  register,
  verifyEmail,
  resendVerificationEmail,
  login,
  forgotPassword,
  resetPassword,
  getMe,
  updateMe,
  requestEmailUpdate,
  verifyEmailUpdate,
  updatePassword,
} = require("../controllers/userController");


const { protect } = require("../middleware/authMiddleware");
const { authLimiter, forgotPasswordLimiter } = require("../utils/rateLimiter");

router.post("/register", authLimiter, registerValidator, register);
router.put("/verify-email/:token", verifyEmailValidator, verifyEmail);
router.post(
  "/resend-verification-email",
  resendVerificationValidator,
  resendVerificationEmail
);
router.post("/login", authLimiter, loginValidator, login);
router.post(
  "/forgotPassword",
  forgotPasswordLimiter,
  forgotPasswordValidator,
  forgotPassword
);
router.put(
  "/resetPassword/:token",
  forgotPasswordLimiter,
  resetPasswordValidator,
  resetPassword
);
router.get("/me", protect, getMe);
router.put("/update-me", protect, updateMeValidator, updateMe);
router.post(
  "/request-email-update",
  protect,
  requestEmailUpdateValidator,
  requestEmailUpdate
);
router.put(
  "/verify-email-update/:token",
  protect,
  authLimiter,
  verifyEmailUpdateValidator,
  verifyEmailUpdate
);
router.put(
  "/update-my-password",
  protect,
  updatePasswordValidator,
  updatePassword
);


module.exports = router;
