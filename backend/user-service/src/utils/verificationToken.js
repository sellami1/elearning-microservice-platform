const crypto = require("crypto");

/**
 * @desc    Generate and hash verification token
 */
exports.generateToken = () => {
  const rawToken = crypto.randomBytes(32).toString("hex");

  const hashedToken = crypto
    .createHash("sha256")
    .update(rawToken)
    .digest("hex");

  return { rawToken, hashedToken };
};

/**
 * @desc    Hash token
 */
exports.hashToken = (token) =>
  crypto.createHash("sha256").update(token).digest("hex");
