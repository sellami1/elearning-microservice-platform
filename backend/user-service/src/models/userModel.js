const mongoose = require("mongoose");
const bcrypt = require("bcryptjs");

const userSchema = new mongoose.Schema(
  {
    email: {
      type: String,
      required: [true, "Email address is required."],
      unique: [true, "Email address must be unique."],
      lowercase: true,
      trim: true,
    },
    password: {
      type: String,
      required: [true, "Password is required."],
      minlength: [8, "Password is too short."],
      select: false,
    },
    role: {
      type: String,
      required: [true, "Role is required."],
      enum: ["learner", "instructor"],
      default: "learner",
      trim: true,
    },
    profile: {
      firstName: {
        type: String,
        required: [true, "First name is required."],
        trim: true,
      },
      lastName: {
        type: String,
        required: [true, "Last name is required."],
        trim: true,
      },
      phone: {
        type: String,
        required: [true, "Phone number is required."],
        trim: true,
      },
      avatar: {
        type: String,
        required: [true, "avatar is required."],
        default: "/media/users/default-avatar.jpg",
        trim: true,
      },
      dateOfBirth: Date,
    },
    address: {
      street: {
        type: String,
        required: [true, "Street is required."],
        trim: true,
      },
      city: {
        type: String,
        required: [true, "City is required."],
        trim: true,
      },
      state: {
        type: String,
        required: [true, "State is required."],
        trim: true,
      },
      country: {
        type: String,
        required: [true, "Country is required."],
        trim: true,
      },
      zipCode: {
        type: String,
        required: [true, "Zip code is required."],
        trim: true,
      },
    },
    isVerified: {
      type: Boolean,
      default: false,
    },
    lastLogin: Date,
    emailVerificationToken: String,
    emailVerificationTokenExpires: Date,
    passwordChangedAt: Date,
    passwordResetToken: String,
    passwordResetTokenExpires: Date,
    pendingEmail: { type: String, trim: true, lowercase: true },
    emailUpdateToken: String,
    emailUpdateTokenExpires: Date,
  },
  {
    timestamps: true,
    versionKey: false,
  }
);

userSchema.index({ role: 1 });

/**
 * @access private
 * @desc Automatically hashes the password before it is saved to MongoDB.
 */
userSchema.pre("save", async function (next) {
  if (!this.isModified("password")) return next();
  const salt = await bcrypt.genSalt(10);
  this.password = await bcrypt.hash(this.password, salt);
  next();
});

/**
 * @desc Validates a login attempt by comparing a plain text password to the hash.
 * @param {string} candidatePassword - The raw password from the login request.
 * @returns {Promise<boolean>} - Resolves to true if password matches.
 */
userSchema.methods.comparePassword = async function (candidatePassword) {
  return await bcrypt.compare(candidatePassword, this.password);
};

/**
 * @desc Automatically prepend base URL to avatar path after document initialization
 */
userSchema.post("init", function (doc) {
  if (doc.profile?.avatar && !doc.profile.avatar.startsWith("http")) {
    const baseUrl = process.env.USER_BACKEND_URL || "http://localhost:8002";
    doc.profile.avatar = `${baseUrl}${doc.profile.avatar}`;
  }
});

// Create model based on the schema
const User = mongoose.model("User", userSchema);
module.exports = User;
