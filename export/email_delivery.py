"""
Email Delivery - Sends generated reports via email

Handles SMTP configuration and sends reports with attachments
to stakeholders automatically.
"""

import logging
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import List, Optional
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class EmailDelivery:
    """Handle email delivery of generated reports."""

    def __init__(self):
        """Initialize email delivery with SMTP configuration."""
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.use_tls = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'

        if not self.sender_email or not self.sender_password:
            logger.warning(
                "Email credentials not configured. "
                "Set SENDER_EMAIL and SENDER_PASSWORD environment variables."
            )

    def send_report(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None,
        cc_emails: Optional[List[str]] = None
    ) -> bool:
        """
        Send report via email with attachments.

        Args:
            recipient_email: Primary recipient email
            subject: Email subject line
            body: Email body text
            attachments: List of file paths to attach
            cc_emails: List of CC email addresses

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.sender_email or not self.sender_password:
            logger.error("Email credentials not configured. Cannot send report.")
            return False

        try:
            # Create message
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = recipient_email
            message['Subject'] = subject

            if cc_emails:
                message['Cc'] = ', '.join(cc_emails)

            # Add body
            message.attach(MIMEText(body, 'plain'))

            # Add attachments
            if attachments:
                for file_path in attachments:
                    if file_path and Path(file_path).exists():
                        self._attach_file(message, file_path)

            # Send email
            self._send_smtp(message, recipient_email, cc_emails)
            logger.info(f"Report sent to {recipient_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    def _attach_file(self, message: MIMEMultipart, file_path: str):
        """Attach file to email message."""
        try:
            file_path = Path(file_path)
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())

            from email import encoders
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {file_path.name}'
            )
            message.attach(part)
            logger.debug(f"Attached file: {file_path.name}")

        except Exception as e:
            logger.warning(f"Failed to attach file {file_path}: {str(e)}")

    def _send_smtp(
        self,
        message: MIMEMultipart,
        recipient_email: str,
        cc_emails: Optional[List[str]] = None
    ):
        """Send message via SMTP server."""
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            if self.use_tls:
                server.starttls()

            server.login(self.sender_email, self.sender_password)

            # Collect all recipients
            recipients = [recipient_email]
            if cc_emails:
                recipients.extend(cc_emails)

            server.sendmail(self.sender_email, recipients, message.as_string())

    def send_bulk_reports(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None
    ) -> dict:
        """
        Send report to multiple recipients.

        Args:
            recipients: List of email addresses
            subject: Email subject
            body: Email body
            attachments: Files to attach

        Returns:
            Dictionary with send status for each recipient
        """
        results = {}
        for email in recipients:
            results[email] = self.send_report(
                recipient_email=email,
                subject=subject,
                body=body,
                attachments=attachments
            )
        return results

    @staticmethod
    def create_email_template(
        report_name: str,
        key_findings: List[str],
        dashboard_url: Optional[str] = None,
        next_run: Optional[str] = None
    ) -> str:
        """
        Create a professional email template.

        Args:
            report_name: Name of the report
            key_findings: List of key findings from the report
            dashboard_url: Optional link to dashboard
            next_run: When next report will run

        Returns:
            Formatted email body
        """
        findings_text = '\n'.join([f'• {finding}' for finding in key_findings])

        email_body = f"""
Hello,

Your {report_name} is ready for review.

KEY FINDINGS:
{findings_text}

FILES INCLUDED:
• data.csv - Complete dataset for further analysis
• report.html - Interactive report with visualizations
• metadata.json - Data schema and record count

ACTION ITEMS:
1. Download and review the attached files
2. Share findings with your team
3. Use the data for strategic decisions

"""
        if dashboard_url:
            email_body += f"VIEW DASHBOARD: {dashboard_url}\n\n"

        if next_run:
            email_body += f"Next report scheduled for: {next_run}\n\n"

        email_body += """Questions?
Contact the analytics team.

---
This report was generated automatically by the analytics platform.
"""
        return email_body
