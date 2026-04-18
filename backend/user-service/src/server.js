const express = require("express");
const dotenv = require("dotenv");
const path = require("path");
dotenv.config({ path: path.resolve(__dirname, "../.env") });
const morgan = require("morgan");
const swaggerUi = require("swagger-ui-express");
const swaggerJsdoc = require("swagger-jsdoc");
const cors = require("cors");
const compression = require("compression");
const mongoSanitize = require("express-mongo-sanitize");
const { xss } = require("express-xss-sanitizer");
const ApiError = require("./utils/apiError");
const globalError = require("./middleware/errorMiddleware");
const dbConnection = require("./config/db");
const mountRoutes = require("./routes");
// const { globalLimiter } = require("./utils/rateLimiter");
const { logger, isDevEnv } = require("./utils/logger");

dbConnection();
const app = express();

const swaggerOptions = {
  definition: {
    openapi: "3.0.3",
    info: {
      title: process.env.USER_BACKEND_APP_NAME || "User Service API",
      version: process.env.USER_BACKEND_APP_VERSION || "1.0.0",
      description: "Auto-generated API documentation for the user service",
    },
    servers: [
      {
        url: `http://localhost:${process.env.USER_BACKEND_PORT || 8002}`,
        description: "Local development server",
      },
    ],
    components: {
      securitySchemes: {
        bearerAuth: {
          type: "http",
          scheme: "bearer",
          bearerFormat: "JWT",
        },
      },
      schemas: {
        UserProfile: {
          type: "object",
          properties: {
            firstName: { type: "string" },
            lastName: { type: "string" },
            phone: { type: "string" },
            avatar: { type: "string", nullable: true },
            dateOfBirth: { type: "string", format: "date", nullable: true },
          },
        },
        UserAddress: {
          type: "object",
          properties: {
            street: { type: "string" },
            city: { type: "string" },
            state: { type: "string" },
            country: { type: "string" },
            zipCode: { type: "string" },
          },
        },
        UserEntity: {
          type: "object",
          properties: {
            _id: { type: "string" },
            email: { type: "string", format: "email" },
            role: { type: "string", enum: ["learner", "instructor"] },
            profile: { $ref: "#/components/schemas/UserProfile" },
            address: { $ref: "#/components/schemas/UserAddress" },
            isVerified: { type: "boolean" },
            lastLogin: { type: "string", format: "date-time", nullable: true },
          },
        },
        RegisterRequest: {
          type: "object",
          required: [
            "email",
            "password",
            "passwordConfirm",
            "firstName",
            "lastName",
            "phone",
            "role",
            "dateOfBirth",
            "street",
            "city",
            "state",
            "country",
            "zipCode",
          ],
          properties: {
            email: { type: "string", format: "email" },
            password: { type: "string", format: "password" },
            passwordConfirm: { type: "string", format: "password" },
            firstName: { type: "string" },
            lastName: { type: "string" },
            phone: { type: "string" },
            role: { type: "string", enum: ["learner", "instructor"] },
            dateOfBirth: { type: "string", format: "date" },
            street: { type: "string" },
            city: { type: "string" },
            state: { type: "string" },
            country: { type: "string" },
            zipCode: { type: "string" },
          },
        },
        LoginRequest: {
          type: "object",
          required: ["email", "password"],
          properties: {
            email: { type: "string", format: "email" },
            password: { type: "string", format: "password" },
          },
        },
        UpdateMeRequest: {
          type: "object",
          properties: {
            firstName: { type: "string" },
            lastName: { type: "string" },
            phone: { type: "string" },
            dateOfBirth: { type: "string", format: "date" },
            street: { type: "string" },
            city: { type: "string" },
            state: { type: "string" },
            country: { type: "string" },
            zipCode: { type: "string" },
          },
        },
        RegistrationResponse: {
          type: "object",
          properties: {
            status: { type: "string", example: "success" },
            message: { type: "string" },
            data: { $ref: "#/components/schemas/UserEntity" },
          },
        },
        LoginResponse: {
          type: "object",
          properties: {
            status: { type: "string", example: "success" },
            data: { $ref: "#/components/schemas/UserEntity" },
            token: { type: "string" },
          },
        },
      },
    },
  },
  apis: [path.join(__dirname, "routes", "*.js")],
};

const swaggerSpec = swaggerJsdoc(swaggerOptions);

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

// app.use("/api", globalLimiter);
app.use("/media", express.static(path.join(__dirname, "media")));

app.use("/api-docs", swaggerUi.serve, swaggerUi.setup(swaggerSpec, {
  explorer: true,
  customSiteTitle: "User Service API Docs",
}));

app.get("/api-docs.json", (req, res) => {
  res.setHeader("Content-Type", "application/json");
  res.send(swaggerSpec);
});

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
