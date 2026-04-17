const request = require("supertest");
const express = require("express");
const User = require("../src/models/userModel");
const createToken = require("../src/utils/createJWT");

process.env.USER_BACKEND_JWT_SECRET_KEY = "test_secret_key";
process.env.USER_BACKEND_JWT_EXPIRE_TIME = "1h";

jest.mock("../src/utils/rateLimiter", () => ({
  globalLimiter: (req, res, next) => next(),
  authLimiter: (req, res, next) => next(),
}));

jest.mock("../src/models/userModel");

const app = express();
app.use(express.json());
require("../src/routes")(app);

app.use((err, req, res, next) => {
  res.status(err.statusCode || 500).json({
    status: err.status || "error",
    message: err.message,
    errors: err.errors,
  });
});

const validPassword = "Password123!";
const userData = {
  email: "test@example.com",
  password: validPassword,
  passwordConfirm: validPassword,
  firstName: "John",
  lastName: "Doe",
  phone: "+12125550123",
  role: "learner",
  dateOfBirth: "1990-01-01",
  street: "Main Street",
  city: "New York",
  state: "NY",
  country: "US",
  zipCode: "10001",
};

const createMockUser = (overrides = {}) => ({
  _id: "507f1f77bcf86cd799439011",
  email: userData.email,
  role: userData.role,
  profile: { firstName: userData.firstName, lastName: userData.lastName },
  address: { country: "US" },
  comparePassword: jest.fn().mockResolvedValue(true),
  save: jest.fn().mockImplementation(function () {
    return Promise.resolve(this);
  }),
  ...overrides,
});

const setupMockQuery = (targetUser) => ({
  select: jest.fn().mockReturnThis(),
  then: jest.fn().mockImplementation((cb) => Promise.resolve(targetUser).then(cb)),
  catch: jest.fn().mockReturnThis(),
});

describe("User Service", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("registers a new user", async () => {
    const createdUser = createMockUser();
    User.findOne.mockReturnValueOnce(setupMockQuery(null));
    User.create.mockResolvedValue(createdUser);
    User.findById.mockResolvedValue(createdUser);

    const res = await request(app).post("/api/v1/users/register").send(userData);

    expect(res.statusCode).toBe(201);
    expect(res.body.status).toBe("success");
  });

  it("logs in a user", async () => {
    const currentUser = createMockUser();
    User.findOne.mockReturnValueOnce(setupMockQuery(currentUser));

    const res = await request(app).post("/api/v1/users/login").send({
      email: userData.email,
      password: validPassword,
    });

    expect(res.statusCode).toBe(200);
    expect(res.body.token).toBeDefined();
  });

  it("returns the current user", async () => {
    const currentUser = createMockUser();
    User.findById.mockResolvedValue(currentUser);
    const token = createToken({ id: currentUser._id, role: currentUser.role });

    const res = await request(app)
      .get("/api/v1/users/me")
      .set("Authorization", `Bearer ${token}`);

    expect(res.statusCode).toBe(200);
    expect(res.body.data.email).toBe(userData.email);
  });

  it("updates the current user profile", async () => {
    const currentUser = createMockUser();
    User.findById.mockResolvedValue(currentUser);
    const token = createToken({ id: currentUser._id, role: currentUser.role });

    const res = await request(app)
      .put("/api/v1/users/update-me")
      .set("Authorization", `Bearer ${token}`)
      .send({ firstName: "Jane" });

    expect(res.statusCode).toBe(200);
    expect(res.body.data.profile.firstName).toBe("Jane");
  });

  it("blocks unauthenticated profile access", async () => {
    const res = await request(app).get("/api/v1/users/me");

    expect(res.statusCode).toBe(401);
  });
});
