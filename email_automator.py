import os
import csv
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class AdvancedEmailAutomator:
    """Production-grade email automator supporting HTML templates,
    attachments, and secure SMTP authentication.
    """

    def __init__(self):
        self.server_host = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.server_port = int(os.getenv("SMTP_PORT", 465))
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")

        self._validate_credentials()

    def _validate_credentials(self):
        """Ensures credentials exist in the environment."""
        if not self.sender_email or not self.sender_password:
            raise ValueError(
                "Missing credentials! Ensure SENDER_EMAIL and "
                "SENDER_PASSWORD are defined in your .env file."
            )

    def _attach_file(self, msg: MIMEMultipart, file_path: Path):
        """Processes and attaches a file to the MIME email object."""
        if not file_path.exists():
            print(f" Warning: Attachment file not found: {file_path}")
            return

        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={file_path.name}",
            )
            msg.attach(part)
            print(f" Attachment loaded: {file_path.name}")
        except Exception as e:
            print(f" Failed to attach file {file_path}: {e}")

    def send_bulk_html_emails(
            self,
            csv_filepath: str,
            subject: str,
            html_template: str,
            attachment_path: str = None
    ):
        """Reads recipient data from CSV and dispatches personalized HTML emails."""
        csv_path = Path(csv_filepath)
        if not csv_path.exists():
            print(f" Error: CSV file '{csv_filepath}' does not exist.")
            return

        print(f" Connecting to SMTP server {self.server_host}:{self.server_port}...")

        try:
            # Using SSL context for secure connection
            with smtplib.SMTP_SSL(self.server_host, self.server_port) as server:
                server.login(self.sender_email, self.sender_password)
                print(" Authentication successful. Commencing dispatch...\n")

                with open(csv_path, mode="r", encoding="utf-8") as file:
                    reader = csv.DictReader(file)

                    sent_count = 0
                    for row in reader:
                        name = row.get("Name", "Student")
                        recipient_email = row.get("Email")

                        if not recipient_email:
                            print(f" Skipping row (missing email): {row}")
                            continue

                        # Container for multipart message
                        msg = MIMEMultipart("mixed")
                        msg["From"] = f"Python Capstone Team <{self.sender_email}>"
                        msg["To"] = recipient_email
                        msg["Subject"] = subject

                        # Render dynamic HTML body
                        formatted_html = html_template.format(name=name)
                        msg.attach(MIMEText(formatted_html, "html"))

                        # Attach file if provided
                        if attachment_path:
                            self._attach_file(msg, Path(attachment_path))

                        # Send email
                        server.send_message(msg)
                        sent_count += 1
                        print(f" [{sent_count}] Successfully sent to {name} ({recipient_email})")

                print(f"\n Finished dispatch! Total emails sent: {sent_count}")

        except smtplib.SMTPAuthenticationError:
            print(" Authentication failed. Check your SENDER_EMAIL and App Password in .env.")
        except Exception as e:
            print(f" An error occurred during transmission: {e}")


# --- Execution ---
if __name__ == "__main__":

    # 1. HTML Email Template
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; max-width: 600px; }}
            .header {{ background-color: #4CAF50; color: white; padding: 10px 15px; border-radius: 5px 5px 0 0; }}
            .content {{ margin-top: 15px; }}
            .badge {{ display: inline-block; background: #e8f5e9; color: #2e7d32; padding: 5px 10px; border-radius: 4px; font-weight: bold; }}
            .footer {{ margin-top: 20px; font-size: 0.85em; color: #777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Python Programming Course</h2>
            </div>
            <div class="content">
                <p>Hello <strong>{name}</strong>,</p>
                <p>Congratulations on reaching <span class="badge">Week 4 – Capstone Project</span>!</p>
                <p>Your automated email tool is working smoothly.</p>
                <p>Keep up the great work!</p>
            </div>
            <div class="footer">
                <p>Automated by Python <code>smtplib</code> & <code>email.mime</code>.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # 2. Instantiate and Run
    try:
        automator = AdvancedEmailAutomator()

        automator.send_bulk_html_emails(
            csv_filepath="students.csv",
            subject="🎉 Capstone Project Update",
            html_template=HTML_TEMPLATE,
            attachment_path=None  # Change to "guidelines.pdf" if you have an attachment
        )
    except ValueError as err:
        print(f" Initialization Error: {err}")