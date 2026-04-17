const express = require("express");
const dotenv = require("dotenv");
const path = require("path");
dotenv.config({ path: path.resolve(__dirname, "../.env") });
const morgan = require("morgan");
const cors = require("cors");
const compression = require("compression");
const mongoSanitize = require("express-mongo-sanitize");
const { xss } = require("express-xss-sanitizer");
const ApiError = require("./utils/apiError");
const globalError = require("./middleware/errorMiddleware");
const dbConnection = require("./config/db");
const mountRoutes = require("./routes");
const { globalLimiter } = require("./utils/rateLimiter");
const { logger, isDevEnv } = require("./utils/logger");

dbConnection();
const app = express();

// app.set('trust proxy', 1);
app.use(cors());
app.options("*", cors());
app.use(compression());

app.use(express.json({ limit: "20kb" }));

// Data Sanitization :
// By default, $ and . characters are removed completely from user-supplied input in the following places:
app.use(mongoSanitize());
app.use(xss());

if (isDevEnv()) {
  app.use(
    morgan("dev", {
      stream: {
        write: (msg) => logger.debug(msg.trim()),
      },
    })
  );
  logger.info(`Dev request logging enabled (mode=${process.env.USER_BACKEND_ENV || process.env.NODE_ENV || "unknown"})`);
}

app.use("/api", globalLimiter);
app.use("/media", express.static(path.join(__dirname, "media")));

mountRoutes(app);

app.all("*", (req, res, next) => {
  next(new ApiError(`Cannot find this route: ${req.originalUrl}`, 400));
});

// Global error handling middleware for express
app.use(globalError);

const PORT = process.env.USER_BACKEND_PORT || 8002;
const server = app.listen(PORT, () => {
  logger.info(`Application running on port ${PORT}`);
});

// Handle rejection outside express
process.on("unhandledRejection", (err) => {
  logger.error(`UnhandledRejection Errors: ${err.name} | ${err.message}`);
  server.close(() => {
    logger.error("Shutting down....");
    process.exit(1);
  });
});
