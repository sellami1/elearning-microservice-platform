const nodemailer = require('nodemailer');

/**
 * @desc    Send email using nodemailer
 */
const sendEmail = async (options) => {
  const isSecure = String(process.env.EMAIL_SECURE).toLowerCase() === 'true';

  // Create transporter ( service that will send email like "gmail","Mailgun", "mialtrap", sendGrid)
  const transporterOptions = {
    host: process.env.EMAIL_HOST,
    port: Number(process.env.EMAIL_PORT),
    secure: isSecure,
  };

  // MailHog does not require auth, while real SMTP providers usually do.
  if (process.env.EMAIL_USER && process.env.EMAIL_PASSWORD) {
    transporterOptions.auth = {
      user: process.env.EMAIL_USER,
      pass: process.env.EMAIL_PASSWORD,
    };
  }

  const transporter = nodemailer.createTransport(transporterOptions);

  const fromAddress =
    process.env.EMAIL_FROM ||
    `${process.env.APP_NAME} <${process.env.EMAIL_USER || 'no-reply@local.test'}>`;

  const mailOpts = {
    from: fromAddress,
    to: options.email,
    subject: options.subject,
    html: options.message,
  };

  await transporter.sendMail(mailOpts);
};

module.exports = sendEmail;
