const jwt = require("jsonwebtoken");
const asyncHandler = require("express-async-handler");
const ApiError = require("../utils/apiError");
const User = require("../models/userModel");

/**
 * @desc   make sure the user is logged in
 */
exports.protect = asyncHandler(async (req, res, next) => {
  const authHeader = req.headers.authorization || req.headers.Authorization;
  let token;

  if (authHeader?.startsWith("Bearer")) {
    token = authHeader.split(" ")[1];
  }

  if (!token)
    return next(
      new ApiError(
        "You are not logged in, please log in to access this route.",
        401
      )
    );

  const decoded = jwt.verify(token, process.env.JWT_SECRET_KEY);
  const currentUser = await User.findById(decoded.userId);
  if (!currentUser)
    return next(
      new ApiError("The user belonging to this token no longer exists.", 401)
    );

  if (!currentUser.isVerified)
    return next(
      new ApiError("Please verify your account to access this route.", 403)
    );

  if (currentUser.passwordChangedAt) {
    const passChangedTimestamp = parseInt(
      currentUser.passwordChangedAt.getTime() / 1000,
      10
    );
    if (passChangedTimestamp > decoded.iat) {
      return next(
        new ApiError(
          "The user recently changed their password. Please log in again.",
          401
        )
      );
    }
  }

  req.user = currentUser;
  next();
});

// /**
//  * @desc   Authorization (User Permissions)
//  * ["admin"]
//  */
// exports.allowedTo = (...roles) =>
//   asyncHandler(async (req, res, next) => {
//     if (!roles.includes(req.user.role)) {
//       return next(
//         new ApiError("You are not authorized to access this route.", 403)
//       );
//     }
//     next();
//   });

// /**
//  * @desc   Middleware function to check if the user is the owner of the profile
//  */
// //
// exports.isProfileOwner = asyncHandler((req, res, next) => {
//   if (req.user._id.toString() === req.params.id) {
//     return next(
//       new ApiError(
//         "You are not authorized to view or edit your profile from here.",
//         403
//       )
//     );
//   }
//   next();
// });
