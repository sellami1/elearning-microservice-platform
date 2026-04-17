const ApiError = require("../utils/apiError");

const isDevMode = () => {
  const nodeEnv = (process.env.NODE_ENV || "").toLowerCase();
  return nodeEnv === "dev" || nodeEnv === "development";
};

const sendErrorForDev = (err, res) =>
  res.status(err.statusCode).json({
    status: err.status,
    error: err,
    message: err.message,
    stack: err.stack,
  });

const sendErrorForProd = (err, res) =>
  res.status(err.statusCode).json({
    status: err.status,
    message: err.message,
  });

const handleJwtInvalidSignature = () =>
  new ApiError("Invalid token, please login again..", 401);

const handleJwtExpired = () =>
  new ApiError("Token expired, please login again..", 401);

/**
 * @desc   Global error handling middleware
 */
const globalError = (err, req, res, next) => {
  err.statusCode = err.statusCode || 500;
  err.status = err.status || "Error";
  if (err.code === 11000) {
    const firstKey = Object.keys(err.keyValue)[0];
    err.message = `This ${firstKey} : '${err.keyValue[firstKey]}' already exists`;
  }
  if (err.name === "JsonWebTokenError") err = handleJwtInvalidSignature();
  if (err.name === "TokenExpiredError") err = handleJwtExpired();
  if (isDevMode()) {
    sendErrorForDev(err, res);
  } else {
    sendErrorForProd(err, res);
  }
};

module.exports = globalError;
