"""
Email service for sending verification and password reset emails.
"""
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template


class EmailService:
    """Professional email service for authentication flows."""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.from_name = os.getenv("FROM_NAME", "RemoteLED Admin")
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost/admin")
        
        # For development: if no SMTP configured, use console logging
        self.dev_mode = not self.smtp_user or not self.smtp_password
        
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send an email via SMTP or log to console in dev mode."""
        
        if self.dev_mode:
            print("\n" + "="*80)
            print(f"📧 EMAIL (DEV MODE - Not actually sent)")
            print("="*80)
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"\n{text_content or html_content}")
            print("="*80 + "\n")
            return True
        
        try:
            message = MIMEMultipart("alternative")
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            message["Subject"] = subject
            
            # Add text and HTML parts
            if text_content:
                message.attach(MIMEText(text_content, "plain"))
            message.attach(MIMEText(html_content, "html"))
            
            # Send via SMTP
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True
            )
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {e}")
            return False
    
    async def send_verification_email(
        self,
        to_email: str,
        verification_token: str
    ) -> bool:
        """Send email verification link."""
        
        verification_url = f"{self.frontend_url}/verify-email?token={verification_token}"
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }
                .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }
                .button { display: inline-block; padding: 12px 30px; background: #667eea; 
                         color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                .footer { text-align: center; margin-top: 20px; color: #666; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚡ RemoteLED Admin</h1>
                </div>
                <div class="content">
                    <h2>Verify Your Email Address</h2>
                    <p>Thank you for registering with RemoteLED Admin Console!</p>
                    <p>Please click the button below to verify your email address:</p>
                    <a href="{{ verification_url }}" class="button">Verify Email Address</a>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #667eea;">{{ verification_url }}</p>
                    <p><strong>This link will expire in 24 hours.</strong></p>
                    <p>If you didn't create an account, you can safely ignore this email.</p>
                </div>
                <div class="footer">
                    <p>© 2025 RemoteLED. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        RemoteLED Admin - Verify Your Email
        
        Thank you for registering!
        
        Please verify your email address by visiting:
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you didn't create an account, you can safely ignore this email.
        """
        
        template = Template(html_template)
        html_content = template.render(verification_url=verification_url)
        
        return await self.send_email(
            to_email=to_email,
            subject="Verify Your RemoteLED Admin Email",
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_password_reset_email(
        self,
        to_email: str,
        reset_token: str
    ) -> bool:
        """Send password reset link."""
        
        reset_url = f"{self.frontend_url}/reset-password?token={reset_token}"
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }
                .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }
                .button { display: inline-block; padding: 12px 30px; background: #667eea; 
                         color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                .warning { background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }
                .footer { text-align: center; margin-top: 20px; color: #666; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚡ RemoteLED Admin</h1>
                </div>
                <div class="content">
                    <h2>Reset Your Password</h2>
                    <p>We received a request to reset your password for your RemoteLED Admin account.</p>
                    <p>Click the button below to reset your password:</p>
                    <a href="{{ reset_url }}" class="button">Reset Password</a>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #667eea;">{{ reset_url }}</p>
                    <div class="warning">
                        <strong>⚠️ Security Notice:</strong>
                        <ul>
                            <li>This link will expire in 1 hour</li>
                            <li>If you didn't request this, please ignore this email</li>
                            <li>Your password won't change until you create a new one</li>
                        </ul>
                    </div>
                </div>
                <div class="footer">
                    <p>© 2025 RemoteLED. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        RemoteLED Admin - Reset Your Password
        
        We received a request to reset your password.
        
        Reset your password by visiting:
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you didn't request this, please ignore this email.
        Your password won't change until you create a new one.
        """
        
        template = Template(html_template)
        html_content = template.render(reset_url=reset_url)
        
        return await self.send_email(
            to_email=to_email,
            subject="Reset Your RemoteLED Admin Password",
            html_content=html_content,
            text_content=text_content
        )


# Singleton instance
email_service = EmailService()


def generate_token() -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(32)

