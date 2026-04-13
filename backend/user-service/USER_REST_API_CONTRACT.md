# User Service REST API Contract

## Service Metadata
- Service: User Service
- Framework: Express.js
- Base API mount: `/api/v1/users`

## Authentication Contract
- Header: `Authorization: Bearer <jwt>`
- JWT secret: `JWT_SECRET_KEY`
- JWT payload fields consumed by middleware:
  - `userId`
  - `role`
- Protected endpoints require:
  - valid JWT
  - existing user
  - `isVerified = true`

## Rate Limiting Contract
- Global limiter on `/api`: 100 requests / 15 minutes
- Auth limiter on selected auth routes: 10 requests / 15 minutes
- Forgot/reset limiter on selected routes: 3 requests / hour
- Exceeded limit response: `429` with API error format

## Content Type
- Request: `application/json`
- Response: `application/json`

## Endpoint Contract
All paths below are relative to `/api/v1/users`.

### POST /register
- Auth: Public
- Middleware: `authLimiter`, `registerValidator`
- Request body:
```json
{
  "email": "user@example.com",
  "password": "StrongPass1!",
  "passwordConfirm": "StrongPass1!",
  "firstName": "John",
  "lastName": "Doe",
  "phone": "+12125550123",
  "role": "learner|instructor",
  "dateOfBirth": "YYYY-MM-DD",
  "street": "string",
  "city": "string",
  "state": "string",
  "country": "US",
  "zipCode": "string"
}
```
- Response 201:
```json
{
  "status": "success",
  "message": "User registered successfully. Please check your email to verify your account."
}
```

### PUT /verify-email/{token}
- Auth: Public
- Middleware: `verifyEmailValidator`
- Path params:
  - `token`: 64-char hex
- Response 200:
```json
{
  "status": "success",
  "message": "Your email has been verified successfully. You can now log in."
}
```
- Errors:
  - `400` invalid/expired token

### POST /resend-verification-email
- Auth: Public
- Middleware: `resendVerificationValidator`
- Request body:
```json
{
  "email": "user@example.com"
}
```
- Response 200:
```json
{
  "status": "success",
  "message": "Verification link has been sent to your email."
}
```
- Privacy-safe behavior: if account does not exist or already verified, response is still 200 with generic message.

### POST /login
- Auth: Public
- Middleware: `authLimiter`, `loginValidator`
- Request body:
```json
{
  "email": "user@example.com",
  "password": "StrongPass1!"
}
```
- Response 200:
```json
{
  "status": "success",
  "data": {
    "_id": "mongo-id",
    "email": "user@example.com",
    "role": "learner|instructor",
    "profile": {
      "firstName": "John",
      "lastName": "Doe",
      "phone": "+12125550123",
      "avatar": "http://.../media/users/default-avatar.jpg",
      "dateOfBirth": "datetime"
    },
    "address": {
      "street": "string",
      "city": "string",
      "state": "string",
      "country": "US",
      "zipCode": "string"
    },
    "isVerified": true,
    "lastLogin": "datetime"
  },
  "token": "jwt"
}
```

### POST /forgotPassword
- Auth: Public
- Middleware: `forgotPasswordLimiter`, `forgotPasswordValidator`
- Request body:
```json
{
  "email": "user@example.com"
}
```
- Response 200:
```json
{
  "status": "success",
  "message": "If an account exists with that email, a reset link has been sent."
}
```

### PUT /resetPassword/{token}
- Auth: Public
- Middleware: `forgotPasswordLimiter`, `resetPasswordValidator`
- Path params:
  - `token`: 64-char hex
- Request body:
```json
{
  "password": "StrongPass1!",
  "passwordConfirm": "StrongPass1!"
}
```
- Response 200:
```json
{
  "status": "success",
  "message": "Your password has been successfully reset",
  "token": "jwt",
  "data": {
    "_id": "mongo-id",
    "email": "user@example.com",
    "role": "learner|instructor"
  }
}
```

### GET /me
- Auth: Private (`protect` middleware)
- Response 200:
```json
{
  "status": "success",
  "data": {
    "_id": "mongo-id",
    "email": "user@example.com",
    "role": "learner|instructor",
    "profile": {
      "firstName": "John",
      "lastName": "Doe",
      "phone": "+12125550123",
      "avatar": "http://...",
      "dateOfBirth": "datetime"
    },
    "address": {
      "street": "string",
      "city": "string",
      "state": "string",
      "country": "US",
      "zipCode": "string"
    }
  }
}
```

### PUT /update-me
- Auth: Private
- Middleware: `updateMeValidator`
- Request body: any subset of profile/address fields
```json
{
  "firstName": "string",
  "lastName": "string",
  "phone": "+12125550123",
  "dateOfBirth": "YYYY-MM-DD",
  "street": "string",
  "city": "string",
  "state": "string",
  "country": "US",
  "zipCode": "string"
}
```
- Response 200:
```json
{
  "status": "success",
  "data": {
    "_id": "mongo-id",
    "email": "user@example.com",
    "role": "learner|instructor"
  }
}
```

### POST /request-email-update
- Auth: Private
- Middleware: `requestEmailUpdateValidator`
- Request body:
```json
{
  "newEmail": "new@example.com",
  "currentPassword": "StrongPass1!"
}
```
- Response 200:
```json
{
  "status": "success",
  "message": "A verification link has been sent to your new email address."
}
```

### PUT /verify-email-update/{token}
- Auth: Private
- Middleware: `authLimiter`, `verifyEmailUpdateValidator`
- Path params:
  - `token`: 64-char hex
- Response 200:
```json
{
  "status": "success",
  "message": "Your email has been updated successfully."
}
```

### PUT /update-my-password
- Auth: Private
- Middleware: `updatePasswordValidator`
- Request body:
```json
{
  "currentPassword": "OldStrongPass1!",
  "password": "NewStrongPass1!",
  "passwordConfirm": "NewStrongPass1!"
}
```
- Response 200:
```json
{
  "status": "success",
  "data": {
    "_id": "mongo-id",
    "email": "user@example.com",
    "role": "learner|instructor"
  },
  "token": "jwt"
}
```

## Error Contract

### Validation errors
- Status: `400`
- Shape:
```json
{
  "errors": [
    {
      "type": "field",
      "msg": "Validation error message",
      "path": "fieldName",
      "location": "body|params"
    }
  ]
}
```

### API/business/auth errors
- Status: varies (`400`, `401`, `403`, `404`, `429`, `500`)
- Shape (production):
```json
{
  "status": "fail|error",
  "message": "Human-readable message"
}
```
