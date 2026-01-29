const { body, param } = require("express-validator");
const validatorMiddleware = require("../../middleware/validatorMiddleware");
const validator = require("validator");
const User = require("../../models/userModel");

exports.registerValidator = [
  body("email")
    .notEmpty()
    .withMessage("Email address is required.")
    .isEmail()
    .withMessage("Invalid email address.")
    .normalizeEmail()
    .custom((val) =>
      User.findOne({ email: val }).then((user) => {
        if (user) {
          return Promise.reject(new Error("Email address is already in use."));
        }
      })
    ),

  body("password")
    .notEmpty()
    .withMessage("Password is required.")
    .isLength({ min: 8 })
    .withMessage("Password must be at least 8 characters long.")
    .isStrongPassword({
      minLength: 8,
      minLowercase: 1,
      minUppercase: 1,
      minNumbers: 1,
      minSymbols: 1,
    })
    .withMessage(
      "Password must contain a lowercase letter, an uppercase letter, a number, and a symbol."
    ),

  body("passwordConfirm")
    .notEmpty()
    .withMessage("Password confirmation is required.")
    .custom((val, { req }) => {
      if (val !== req.body.password) {
        throw new Error("Passwords do not match.");
      }
      return true;
    }),

  body("firstName")
    .trim()
    .notEmpty()
    .withMessage("First name is required.")
    .isLength({ min: 2 })
    .withMessage("First name is too short.")
    .isAlpha("en-US", { ignore: " -" })
    .escape(),

  body("lastName")
    .trim()
    .notEmpty()
    .withMessage("Last name is required.")
    .isLength({ min: 2 })
    .withMessage("Last name is too short.")
    .isAlpha("en-US", { ignore: " -" })
    .escape(),

  body("phone")
    .notEmpty()
    .withMessage("Phone number is required.")
    .isMobilePhone("any", { strictMode: true })
    .withMessage(
      "Invalid phone number. Please include '+' and country code (e.g., +12125550123)."
    ),

  body("role")
    .notEmpty()
    .withMessage("Role is required.")
    .isIn(["learner", "instructor"])
    .withMessage("Invalid role selected."),

  body("dateOfBirth")
    .isISO8601()
    .withMessage("Invalid date format. Use YYYY-MM-DD.")
    .custom((value) => {
      const dob = new Date(value);
      const today = new Date();
      if (dob >= today) {
        throw new Error("Date of birth must be in the past.");
      }
      return true;
    }),

  body("street")
    .trim()
    .notEmpty()
    .withMessage("Street address is required.")
    .isLength({ min: 3 })
    .withMessage("Invalid street name.")
    .escape(),

  body("city")
    .trim()
    .notEmpty()
    .withMessage("City is required.")
    .isLength({ min: 2 })
    .withMessage("Invalid city name.")
    .escape(),

  body("state")
    .trim()
    .notEmpty()
    .withMessage("State/Province is required.")
    .isLength({ min: 2 })
    .withMessage("State name is too short.")
    .escape(),

  body("country")
    .trim()
    .notEmpty()
    .withMessage("Country is required.")
    .isISO31661Alpha2()
    .withMessage("Invalid country code (use 2 letters, e.g., US, TN).")
    .toUpperCase(),

  body("zipCode")
    .trim()
    .notEmpty()
    .withMessage("Zip/Postal code is required.")
    .custom((value, { req }) => {
      const country = req.body.country ? req.body.country.toUpperCase() : "any";
      console.log("country", country);
      if (!validator.isPostalCode(value, country)) {
        throw new Error(`Invalid zip/postal code for ${country}.`);
      }
      return true;
    }),

  validatorMiddleware,
];

exports.verifyEmailValidator = [
  param("token")
    .notEmpty()
    .withMessage("Verification token is required.")
    .isHexadecimal()
    .withMessage("Invalid token format.")
    .isLength({ min: 64, max: 64 })
    .withMessage("Invalid token length."),

  validatorMiddleware,
];

exports.resendVerificationValidator = [
  body("email")
    .trim()
    .notEmpty()
    .withMessage("Email address is required.")
    .isEmail()
    .withMessage("Please provide a valid email address.")
    .normalizeEmail(),

  validatorMiddleware,
];

exports.forgotPasswordValidator = [
  body("email")
    .trim()
    .notEmpty()
    .withMessage("Email address is required.")
    .isEmail()
    .withMessage("Invalid email format.")
    .normalizeEmail(),

  validatorMiddleware,
];

exports.resetPasswordValidator = [
  param("token")
    .notEmpty()
    .withMessage("Reset token is required.")
    .isHexadecimal()
    .withMessage("Invalid token format.")
    .isLength({ min: 64, max: 64 })
    .withMessage("Invalid token length."),

  body("password")
    .notEmpty()
    .withMessage("New password is required.")
    .isStrongPassword({
      minLength: 8,
      minLowercase: 1,
      minUppercase: 1,
      minNumbers: 1,
      minSymbols: 1,
    })
    .withMessage(
      "Password must be 8+ chars with uppercase, lowercase, number, and symbol."
    ),

  body("passwordConfirm")
    .notEmpty()
    .withMessage("Password confirmation is required.")
    .custom((val, { req }) => {
      if (val !== req.body.password) {
        throw new Error("Passwords do not match.");
      }
      return true;
    }),

  validatorMiddleware,
];

exports.loginValidator = [
  body("email")
    .notEmpty()
    .withMessage("Email address is required.")
    .isEmail()
    .withMessage("Invalid email address.")
    .normalizeEmail(),

  body("password").notEmpty().withMessage("Password is required."),

  validatorMiddleware,
];

exports.updateMeValidator = [
  body("firstName")
    .optional()
    .trim()
    .isLength({ min: 2 })
    .withMessage("First name is too short.")
    .isAlpha("en-US", { ignore: " -" })
    .withMessage("First name must contain only letters.")
    .escape(),

  body("lastName")
    .optional()
    .trim()
    .isLength({ min: 2 })
    .withMessage("Last name is too short.")
    .isAlpha("en-US", { ignore: " -" })
    .withMessage("Last name must contain only letters.")
    .escape(),

  body("phone")
    .optional()
    .isMobilePhone("any", { strictMode: true })
    .withMessage(
      "Invalid phone number. Use E.164 format (e.g., +12125550123)."
    ),

  body("dateOfBirth")
    .optional()
    .isISO8601()
    .withMessage("Invalid date format. Use YYYY-MM-DD.")
    .custom((value) => {
      if (new Date(value) >= new Date()) {
        throw new Error("Date of birth must be in the past.");
      }
      return true;
    }),

  body("street")
    .optional()
    .trim()
    .isLength({ min: 3 })
    .withMessage("Invalid street name.")
    .escape(),

  body("city")
    .optional()
    .trim()
    .isLength({ min: 2 })
    .withMessage("Invalid city name.")
    .escape(),

  body("state")
    .optional()
    .trim()
    .isLength({ min: 2 })
    .withMessage("State name is too short.")
    .escape(),

  body("country")
    .optional()
    .trim()
    .isISO31661Alpha2()
    .withMessage("Invalid country code (use 2 letters).")
    .toUpperCase(),

  body("zipCode")
    .optional()
    .trim()
    .custom((value, { req }) => {
      const country = req.body.country ? req.body.country.toUpperCase() : "any";
      if (!validator.isPostalCode(value, country)) {
        throw new Error(`Invalid zip/postal code for ${country}.`);
      }
      return true;
    }),

  validatorMiddleware,
];

exports.requestEmailUpdateValidator = [
  body("newEmail")
    .notEmpty()
    .withMessage("New email is required")
    .isEmail()
    .withMessage("Invalid email format")
    .normalizeEmail(),

  body("currentPassword")
    .notEmpty()
    .withMessage("Current password is required to verify your identity"),

  validatorMiddleware,
];

exports.verifyEmailUpdateValidator = [
  param("token")
    .notEmpty()
    .withMessage("Verification token is required.")
    .isHexadecimal()
    .withMessage("Invalid token format.")
    .isLength({ min: 64, max: 64 })
    .withMessage("Invalid token length."),

  validatorMiddleware,
];

exports.updatePasswordValidator = [
  body("currentPassword")
    .notEmpty()
    .withMessage("Current password is required."),

  body("password")
    .notEmpty()
    .withMessage("New password is required.")
    .isStrongPassword({
      minLength: 8,
      minLowercase: 1,
      minUppercase: 1,
      minNumbers: 1,
      minSymbols: 1,
    })
    .withMessage(
      "Password must be 8+ characters with uppercase, lowercase, number, and symbol."
    ),

  body("passwordConfirm")
    .notEmpty()
    .withMessage("Password confirmation is required.")
    .custom((val, { req }) => {
      if (val !== req.body.password) {
        throw new Error("Passwords do not match.");
      }
      return true;
    }),

  validatorMiddleware,
];
