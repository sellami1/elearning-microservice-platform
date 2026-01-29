const asyncHandler = require("express-async-handler");
const Email = require("../utils/emailTemplate");
const createToken = require("../utils/createJWT");
const ApiError = require("../utils/apiError");
const User = require("../models/userModel");
const { generateToken, hashToken } = require("../utils/verificationToken");

/**
 * @desc    Register new user
 * @route   POST /api/v1/users/register
 * @access  Public
 */
exports.register = asyncHandler(async (req, res, next) => {
  const { rawToken, hashedToken } = generateToken();

  const user = await User.create({
    email: req.body.email,
    password: req.body.password,
    profile: {
      firstName: req.body.firstName,
      lastName: req.body.lastName,
      phone: req.body.phone,
      dateOfBirth: req.body.dateOfBirth,
    },
    role: req.body.role,
    address: {
      street: req.body.street,
      city: req.body.city,
      state: req.body.state,
      country: req.body.country,
      zipCode: req.body.zipCode,
    },
    emailVerificationToken: hashedToken,
    emailVerificationTokenExpires: Date.now() + 5 * 60 * 1000, // 5 min
  });

  const verifyUrl = `${process.env.PUBLIC_FRONTEND_URL}/verify-email/${rawToken}`;
  await Email.verifyEmail(user, verifyUrl);

  res.status(201).json({
    status: "success",
    message:
      "User registered successfully. Please check your email to verify your account.",
  });
});

/**
 * @desc    Resend verification email
 * @route   POST /api/v1/users/resend-verification-email
 * @access  Public
 */
exports.resendVerificationEmail = asyncHandler(async (req, res, next) => {
  const user = await User.findOne({ email: req.body.email });

  if (!user || user.isVerified)
    return res.status(200).json({
      status: "success",
      message:
        "If an account exists with that email, a verification link has been sent.",
    });

  const { rawToken, hashedToken } = generateToken();

  user.emailVerificationToken = hashedToken;
  user.emailVerificationTokenExpires = Date.now() + 5 * 60 * 1000;

  await user.save({ validateBeforeSave: false });

  const verifyUrl = `${process.env.PUBLIC_FRONTEND_URL}/verify-email/${rawToken}`;
  await Email.verifyEmail(user, verifyUrl, "resend");

  res.status(200).json({
    status: "success",
    message: "Verification link has been sent to your email.",
  });
});

/**
 * @desc    Verify email
 * @route   PUT /api/v1/users/verify-email/:token
 * @access  Public
 */
exports.verifyEmail = asyncHandler(async (req, res, next) => {
  const hashedToken = hashToken(req.params.token);

  const user = await User.findOne({
    emailVerificationToken: hashedToken,
    emailVerificationTokenExpires: { $gt: Date.now() },
  });

  if (!user)
    return next(new ApiError("Verification token is invalid or expired", 400));

  user.isVerified = true;
  user.emailVerificationToken = undefined;
  user.emailVerificationTokenExpires = undefined;

  await user.save({ validateBeforeSave: false });

  res.status(200).json({
    status: "success",
    message: "Your email has been verified successfully. You can now log in.",
  });
});

/**
 * @desc    Forgot password
 * @route   POST /api/v1/users/forgotPassword
 * @access  Public
 */
exports.forgotPassword = asyncHandler(async (req, res, next) => {
  const { email } = req.body;

  const user = await User.findOne({ email });

  if (!user || !user.isVerified)
    return res.status(200).json({
      status: "success",
      message:
        "If an account exists with that email, a reset link has been sent.",
    });

  const { rawToken, hashedToken } = generateToken();

  user.passwordResetToken = hashedToken;
  user.passwordResetTokenExpires = Date.now() + 5 * 60 * 1000;

  await user.save({ validateBeforeSave: false });

  const resetUrl = `${process.env.PUBLIC_FRONTEND_URL}/reset-password/${rawToken}`;

  try {
    await Email.forgotPassword(user, resetUrl);
  } catch (err) {
    user.passwordResetToken = undefined;
    user.passwordResetTokenExpires = undefined;
    await user.save({ validateBeforeSave: false });

    return next(new ApiError("Email sending failed. Try again later!", 500));
  }

  res.status(200).json({
    status: "success",
    message:
      "If an account exists with that email, a reset link has been sent.",
  });
});

/**
 * @desc    Reset password
 * @route   PUT /auth/resetPassword/:token
 * @access  Public
 */
exports.resetPassword = asyncHandler(async (req, res, next) => {
  const hashedResetToken = hashToken(req.params.token);

  const user = await User.findOne({
    passwordResetToken: hashedResetToken,
    passwordResetTokenExpires: { $gt: Date.now() },
  });

  if (!user) return next(new ApiError("Token is invalid or has expired", 400));

  if (!user.isVerified)
    return next(
      new ApiError("Account is not eligible for password reset.", 403)
    );

  user.password = req.body.password;
  user.passwordResetToken = undefined;
  user.passwordResetTokenExpires = undefined;
  user.passwordChangedAt = Date.now();
  user.lastLogin = Date.now();

  await user.save();
  user.password = undefined;
  await Email.passwordChanged(user);

  const token = createToken({ id: user._id, role: user.role });

  res.status(200).json({
    status: "success",
    message: "Your password has been successfully reset",
    token,
    data: user,
  });
});

/**
 * @desc    Login
 * @route   POST /api/v1/users/login
 * @access  Public
 */
exports.login = asyncHandler(async (req, res, next) => {
  const user = await User.findOne({
    email: req.body.email
  }).select("+password");

  if (!user || !(await user.comparePassword(req.body.password)))
    return next(new ApiError("Incorrect email or password", 401));

  if (!user.isVerified)
    return next(
      new ApiError("Please verify your email before logging in.", 401)
    );

  user.lastLogin = Date.now();
  await user.save({ validateBeforeSave: false });
  await Email.newLoginDetected(user, {
    ip: req.ip,
    userAgent: req.headers["user-agent"],
  });
  const token = createToken({ id: user._id, role: user.role });
  user.password = undefined;

  res.status(200).json({ status: "success", data: user, token });
});

/**
 * @desc    Get current user
 * @route   GET /api/v1/users/me
 * @access  Private
 */
exports.getMe = asyncHandler(async (req, res, next) => {
  res.status(200).json({
    status: "success",
    data: req.user,
  });
});

/**
 * @desc    Update current user profile and address
 * @route   PUT /api/v1/users/update-me
 * @access  Private
 */
exports.updateMe = asyncHandler(async (req, res, next) => {
  const user = req.user;

  const profileFields = ["firstName", "lastName", "phone", "dateOfBirth"];
  const addressFields = ["street", "city", "state", "country", "zipCode"];

  profileFields.forEach((field) => {
    if (req.body[field] !== undefined) user.profile[field] = req.body[field];
  });

  addressFields.forEach((field) => {
    if (req.body[field] !== undefined) user.address[field] = req.body[field];
  });

  await user.save({ validateBeforeSave: true });

  res.status(200).json({
    status: "success",
    data: user,
  });
});

/**
 * @desc    Request email change
 * @route   POST /api/v1/users/request-email-update
 * @access  Private
 */
exports.requestEmailUpdate = asyncHandler(async (req, res, next) => {
  const { newEmail, currentPassword } = req.body;

  const user = await User.findById(req.user._id).select("+password");

  if (!(await user.comparePassword(currentPassword)))
    return next(new ApiError("Incorrect current password", 401));

  const emailExists = await User.findOne({ email: newEmail });
  if (emailExists) return next(new ApiError("Email is already in use", 400));

  const { rawToken, hashedToken } = generateToken();

  user.pendingEmail = newEmail;
  user.emailUpdateToken = hashedToken;
  user.emailUpdateTokenExpires = Date.now() + 5 * 60 * 1000;
  await user.save({ validateBeforeSave: false });
  user.password = undefined;

  const verifyUrl = `${process.env.PUBLIC_FRONTEND_URL}/verify-email-update/${rawToken}`;
  await Email.sendEmailUpdateLink(newEmail, user, verifyUrl);

  res.status(200).json({
    status: "success",
    message: "A verification link has been sent to your new email address.",
  });
});

/**
 * @desc    Confirm and update email
 * @route   PUT /api/v1/users/verify-email-update/:token
 * @access  Private
 */
exports.verifyEmailUpdate = asyncHandler(async (req, res, next) => {
  const hashedToken = hashToken(req.params.token);

  const user = await User.findOne({
    emailUpdateToken: hashedToken,
    emailUpdateTokenExpires: { $gt: Date.now() },
  });

  if (!user) return next(new ApiError("Token is invalid or has expired", 400));

  const oldEmail = user.email;

  user.email = user.pendingEmail;
  user.pendingEmail = undefined;
  user.emailUpdateToken = undefined;
  user.emailUpdateTokenExpires = undefined;

  await user.save({ validateBeforeSave: false });
  await Email.notifyEmailChanged(oldEmail, user);

  res.status(200).json({
    status: "success",
    message: "Your email has been updated successfully.",
  });
});

/**
 * @desc    Update logged user password
 * @route   PUT /api/v1/users/update-my-password
 * @access  Private
 */
exports.updatePassword = asyncHandler(async (req, res, next) => {
  const user = await User.findById(req.user._id).select("+password");

  if (!(await user.comparePassword(req.body.currentPassword)))
    return next(new ApiError("Your current password is incorrect", 401));

  user.password = req.body.password;
  user.passwordChangedAt = Date.now();
  await user.save();
  const token = createToken({ id: user._id, role: user.role });
  await Email.passwordChanged(user);
  user.password = undefined;

  res.status(200).json({ status: "success", data: user, token });
});