const express = require("express");
const dotenv = require("dotenv");
dotenv.config({ path: "../../.env" });
const path = require("path");
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

if (process.env.USER_BACKEND_ENV === "development") {
  app.use(morgan("dev"));
  console.log(`mode: ${process.env.USER_BACKEND_ENV}`);
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
  console.log(`Application running on port ${PORT}`);
});

// Handle rejection outside express
process.on("unhandledRejection", (err) => {
  console.error(`UnhandledRejection Errors: ${err.name} | ${err.message}`);
  server.close(() => {
    console.error(`Shutting down....`);
    process.exit(1);
  });
});
