const isDevEnv = () => {
  const env = (process.env.USER_BACKEND_ENV || process.env.NODE_ENV || "").toLowerCase();
  return env === "dev" || env === "development";
};

const formatMessage = (level, message) => {
  const runtime = process.env.USER_BACKEND_ENV || process.env.NODE_ENV || "unknown";
  return `${new Date().toISOString()} | ${level} | user-service | env=${runtime} | ${message}`;
};

const logger = {
  debug: (message) => {
    if (isDevEnv()) {
      console.debug(formatMessage("DEBUG", message));
    }
  },
  info: (message) => {
    console.log(formatMessage("INFO", message));
  },
  warn: (message) => {
    console.warn(formatMessage("WARN", message));
  },
  error: (message) => {
    console.error(formatMessage("ERROR", message));
  },
};

module.exports = {
  logger,
  isDevEnv,
};
