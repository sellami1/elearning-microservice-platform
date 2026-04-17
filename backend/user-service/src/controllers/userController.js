const asyncHandler = require("express-async-handler");
const createToken = require("../utils/createJWT");
const ApiError = require("../utils/apiError");
const User = require("../models/userModel");

/**
 * @desc    Register new user
 * @route   POST /api/v1/users/register
 * @access  Public
 */
exports.register = asyncHandler(async (req, res) => {
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
  });

  const responseUser = await User.findById(user._id);

  res.status(201).json({
    status: "success",
    message: "User registered successfully.",
    data: responseUser,
  });
});

/**
 * @desc    Login
 * @route   POST /api/v1/users/login
 * @access  Public
 */
exports.login = asyncHandler(async (req, res, next) => {
  const user = await User.findOne({
    email: req.body.email,
  }).select("+password");

  if (!user || !(await user.comparePassword(req.body.password))) {
    return next(new ApiError("Incorrect email or password", 401));
  }

  user.lastLogin = Date.now();
  await user.save({ validateBeforeSave: false });

  const token = createToken({ id: user._id, role: user.role });
  user.password = undefined;

  res.status(200).json({ status: "success", data: user, token });
});

/**
 * @desc    Get current user
 * @route   GET /api/v1/users/me
 * @access  Private
 */
exports.getMe = asyncHandler(async (req, res) => {
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
exports.updateMe = asyncHandler(async (req, res) => {
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
