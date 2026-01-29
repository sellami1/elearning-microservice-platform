const jwt = require("jsonwebtoken");

/**
 * @desc   Create JWT token
 */
const createToken = (payload) =>
  jwt.sign(
    { userId: payload.id, role: payload.role },
    process.env.JWT_SECRET_KEY,
    {
      expiresIn: process.env.JWT_EXPIRE_TIME,
    }
  );

module.exports = createToken;
