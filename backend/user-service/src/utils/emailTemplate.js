const sendEmail = require("./sendEmail");

/**
 * @desc    Email verification
 */
exports.verifyEmail = async (user, verifyUrl, action = null) => {
  const subject =
    action === "resend"
      ? "Resend: Verify your email address"
      : "Verify your email address";
  return sendEmail({
    email: user.email,
    subject: subject,
    message: `
<!DOCTYPE html>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8f9fa; color: #333;">
  <table role="presentation" style="width: 100%; max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
    <tr>
      <td style="padding: 40px 30px;">
        <h1 style="margin: 0 0 20px; font-size: 24px; font-weight: 600; color: #1a1a1a; text-align: center;">Verify Your Email Address</h1>
        <p style="margin: 0 0 20px; line-height: 1.6; font-size: 16px; color: #555;">Hello ${user.profile.firstName} ${user.profile.lastName},</p>
        <p style="margin: 0 0 30px; line-height: 1.6; font-size: 16px; color: #555;">Please verify your email address by clicking the button below. This link will expire in 5 minutes.</p>
        <table role="presentation" style="margin: 0 auto;">
          <tr>
            <td style="text-align: center;">
              <a href="${verifyUrl}" style="display: inline-block; padding: 12px 24px; background-color: #007bff; color: #ffffff; text-decoration: none; font-weight: 500; border-radius: 6px; font-size: 16px;">Verify Email</a>
            </td>
          </tr>
        </table>
        <p style="margin: 30px 0 0; font-size: 14px; color: #888; text-align: center; line-height: 1.5;">If the button doesn't work, copy and paste this link into your browser: <br><a href="${verifyUrl}" style="color: #007bff;">${verifyUrl}</a></p>
      </td>
    </tr>
    <tr>
      <td style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; font-size: 12px; color: #6c757d;">
        &copy; ${new Date().getFullYear()} ${process.env.APP_NAME}. All rights reserved.
      </td>
    </tr>
  </table>
</body>
    `,
  });
};

/**
 * @desc    Forgot password
 */
exports.forgotPassword = async (user, resetUrl) => {
  return sendEmail({
    email: user.email,
    subject: "Password reset request",
    message: `
<!DOCTYPE html>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8f9fa; color: #333;">
  <table role="presentation" style="width: 100%; max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
    <tr>
      <td style="padding: 40px 30px;">
        <h1 style="margin: 0 0 20px; font-size: 24px; font-weight: 600; color: #1a1a1a; text-align: center;">Reset Your Password</h1>
        <p style="margin: 0 0 20px; line-height: 1.6; font-size: 16px; color: #555;">Hello ${user.profile.firstName} ${user.profile.lastName},</p>
        <p style="margin: 0 0 30px; line-height: 1.6; font-size: 16px; color: #555;">You requested a password reset. Click the button below to set a new password. This link will expire in 5 minutes.</p>
        <table role="presentation" style="margin: 0 auto;">
          <tr>
            <td style="text-align: center;">
              <a href="${resetUrl}" style="display: inline-block; padding: 12px 24px; background-color: #007bff; color: #ffffff; text-decoration: none; font-weight: 500; border-radius: 6px; font-size: 16px;">Reset Password</a>
            </td>
          </tr>
        </table>
        <p style="margin: 30px 0 0; font-size: 14px; color: #888; text-align: center; line-height: 1.5;">If you did not request this, please ignore this email. <br><a href="${resetUrl}" style="color: #007bff;">${resetUrl}</a></p>
      </td>
    </tr>
    <tr>
      <td style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; font-size: 12px; color: #6c757d;">
        &copy; ${new Date().getFullYear()} ${process.env.APP_NAME}. All rights reserved.
      </td>
    </tr>
  </table>
</body>
    `,
  });
};

/**
 * @desc    Password changed (reset or update)
 */
exports.passwordChanged = async (user) => {
  return sendEmail({
    email: user.email,
    subject: "Your password has been changed",
    message: `
<!DOCTYPE html>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8f9fa; color: #333;">
  <table role="presentation" style="width: 100%; max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
    <tr>
      <td style="padding: 40px 30px;">
        <h1 style="margin: 0 0 20px; font-size: 24px; font-weight: 600; color: #1a1a1a; text-align: center;">Password Updated</h1>
        <p style="margin: 0 0 20px; line-height: 1.6; font-size: 16px; color: #555;">Hello ${user.profile.firstName} ${user.profile.lastName},</p>
        <p style="margin: 0 0 30px; line-height: 1.6; font-size: 16px; color: #555;">Your account password was recently changed.</p>
        <p style="margin: 0 0 20px; line-height: 1.6; font-size: 16px; color: #dc3545; font-weight: 500;">If this was not you, please contact support immediately to secure your account.</p>
        <table role="presentation" style="margin: 0 auto;">
          <tr>
            <td style="text-align: center;">
              <a href="mailto:mbarkihoussem99@gmail.com" style="display: inline-block; padding: 12px 24px; background-color: #dc3545; color: #ffffff; text-decoration: none; font-weight: 500; border-radius: 6px; font-size: 16px;">Contact Support</a>
            </td>
          </tr>
        </table>
      </td>
    </tr>
    <tr>
      <td style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; font-size: 12px; color: #6c757d;">
        &copy; ${new Date().getFullYear()} ${process.env.APP_NAME}. All rights reserved.
      </td>
    </tr>
  </table>
</body>
    `,
  });
};

/**
 * @desc    New login detected
 */
exports.newLoginDetected = async (user, meta = {}) => {
  const {
    ip = "Unknown IP",
    userAgent = "Unknown device",
    time = new Date().toLocaleString(),
  } = meta;

  return sendEmail({
    email: user.email,
    subject: "New login detected on your account",
    message: `
<!DOCTYPE html>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8f9fa; color: #333;">
  <table role="presentation" style="width: 100%; max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
    <tr>
      <td style="padding: 40px 30px;">
        <h1 style="margin: 0 0 20px; font-size: 24px; font-weight: 600; color: #1a1a1a; text-align: center;">New Login Detected</h1>
        <p style="margin: 0 0 20px; line-height: 1.6; font-size: 16px; color: #555;">Hello ${user.profile.firstName} ${user.profile.lastName},</p>
        <p style="margin: 0 0 30px; line-height: 1.6; font-size: 16px; color: #555;">We detected a new login to your account. If this was you, no action is needed.</p>
        <h2 style="margin: 0 0 15px; font-size: 18px; font-weight: 600; color: #1a1a1a;">Login Details</h2>
        <ul style="margin: 0 0 30px; padding-left: 20px; line-height: 1.6; font-size: 16px; color: #555;">
          <li style="margin-bottom: 10px;">Date & Time: <strong>${time}</strong></li>
          <li style="margin-bottom: 10px;">IP Address: <strong>${ip}</strong></li>
          <li style="margin-bottom: 0;">Device / Browser: <strong>${userAgent}</strong></li>
        </ul>
        <p style="margin: 0 0 20px; line-height: 1.6; font-size: 16px; color: #dc3545; font-weight: 500;">If you do NOT recognize this login:</p>
        <ul style="margin: 0 0 30px; padding-left: 20px; line-height: 1.6; font-size: 16px; color: #555;">
          <li style="margin-bottom: 10px;">Change your password immediately</li>
          <li style="margin-bottom: 0;">Contact support as soon as possible</li>
        </ul>
        <table role="presentation" style="margin: 0 auto;">
          <tr>
            <td style="text-align: center;">
              <a href="mailto:mbarkihoussem99@gmail.com" style="display: inline-block; padding: 12px 24px; background-color: #dc3545; color: #ffffff; text-decoration: none; font-weight: 500; border-radius: 6px; font-size: 16px; margin-right: 10px;">Contact Support</a>
              <a href="${process.env.PUBLIC_FRONTEND_URL}/change-password" style="display: inline-block; padding: 12px 24px; background-color: #007bff; color: #ffffff; text-decoration: none; font-weight: 500; border-radius: 6px; font-size: 16px;">Change Password</a>
            </td>
          </tr>
        </table>
      </td>
    </tr>
    <tr>
      <td style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; font-size: 12px; color: #6c757d;">
        Stay safe,<br>Security Team &copy; ${new Date().getFullYear()} ${process.env.APP_NAME}. All rights reserved.
      </td>
    </tr>
  </table>
</body>
    `,
  });
};

/**
 * @desc Send link to verify new email address with consistent branding
 */
exports.sendEmailUpdateLink = async (newEmail, user, verifyUrl) => {
  return sendEmail({
    email: newEmail,
    subject: "Confirm your new email address",
    message: `
<!DOCTYPE html>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8f9fa; color: #333;">
  <table role="presentation" style="width: 100%; max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
    <tr>
      <td style="padding: 40px 30px;">
        <h1 style="margin: 0 0 20px; font-size: 24px; font-weight: 600; color: #1a1a1a; text-align: center;">Confirm Email Change</h1>
        <p style="margin: 0 0 20px; line-height: 1.6; font-size: 16px; color: #555;">Hello ${user.profile.firstName} ${user.profile.lastName},</p>
        <p style="margin: 0 0 30px; line-height: 1.6; font-size: 16px; color: #555;">You requested to change your email address. Please click the button below to confirm <strong>${newEmail}</strong> as your new primary email. This link will expire in 5 minutes.</p>
        <table role="presentation" style="margin: 0 auto;">
          <tr>
            <td style="text-align: center;">
              <a href="${verifyUrl}" style="display: inline-block; padding: 12px 24px; background-color: #007bff; color: #ffffff; text-decoration: none; font-weight: 500; border-radius: 6px; font-size: 16px;">Confirm New Email</a>
            </td>
          </tr>
        </table>
        <p style="margin: 30px 0 0; font-size: 14px; color: #888; text-align: center; line-height: 1.5;">If the button doesn't work, copy and paste this link into your browser: <br><a href="${verifyUrl}" style="color: #007bff;">${verifyUrl}</a></p>
      </td>
    </tr>
    <tr>
      <td style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; font-size: 12px; color: #6c757d;">
        &copy; ${new Date().getFullYear()} ${process.env.APP_NAME}. All rights reserved.
      </td>
    </tr>
  </table>
</body>
    `,
  });
};

/**
 * @desc Notify old email address that the account email has been changed
 */
exports.notifyEmailChanged = async (oldEmail, user) => {
  return sendEmail({
    email: oldEmail,
    subject: "Security Alert: Your email has been changed",
    message: `
<!DOCTYPE html>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8f9fa; color: #333;">
  <table role="presentation" style="width: 100%; max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
    <tr>
      <td style="padding: 40px 30px;">
        <h1 style="margin: 0 0 20px; font-size: 24px; font-weight: 600; color: #d9534f; text-align: center;">Security Notification</h1>
        <p style="margin: 0 0 20px; line-height: 1.6; font-size: 16px; color: #555;">Hello ${user.profile.firstName} ${user.profile.lastName},</p>
        <p style="margin: 0 0 20px; line-height: 1.6; font-size: 16px; color: #555;">This is a security alert to inform you that the email address for your ${process.env.APP_NAME} account has been successfully changed to <strong>${user.email}</strong>.</p>
        <div style="background-color: #fff3cd; border: 1px solid #ffeeba; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
          <p style="margin: 0; font-size: 14px; color: #856404;"><strong>If you did not make this change:</strong> Please contact our support team immediately to secure your account.</p>
        </div>
        <p style="margin: 0; line-height: 1.6; font-size: 16px; color: #555;">If you did perform this change, you can safely ignore this email.</p>
      </td>
    </tr>
    <tr>
      <td style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; font-size: 12px; color: #6c757d;">
        &copy; ${new Date().getFullYear()} ${process.env.APP_NAME}. All rights reserved.
      </td>
    </tr>
  </table>
</body>
    `,
  });
};
