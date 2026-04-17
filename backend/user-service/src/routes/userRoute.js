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
const { authLimiter } = require("../utils/rateLimiter");

router.post("/register", authLimiter, registerValidator, register);
router.post("/login", authLimiter, loginValidator, login);
router.get("/me", protect, getMe);
router.put("/update-me", protect, updateMeValidator, updateMe);

module.exports = router;
