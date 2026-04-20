const jwt = require("jsonwebtoken");

/**
 * @desc   Create JWT token
 */
const createToken = (payload) =>
  jwt.sign(
    { userId: payload.id, role: payload.role },
    process.env.USER_BACKEND_JWT_SECRET_KEY
  );

module.exports = createToken;
