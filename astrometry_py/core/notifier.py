import smtplib
from email.message import EmailMessage
import requests

def send_slack_notification(message: str, webhook_url: str):
    """
    Sends a notification message to a Slack channel via webhook.
    """
    payload = {"text": message}
    try:
        # requests.post(webhook_url, json=payload)
        print(payload)
    except Exception as e:
        print(f"Error sending Slack notification: {e}")

def send_discord_notification(message: str, webhook_url: str):
    """
    Sends a notification message to a Discord channel via webhook.
    """
    payload = {"content": message}
    try:
        # requests.post(webhook_url, json=payload)
        print(payload)
    except Exception as e:
        print(f"Error sending Discord notification: {e}")

def send_email_notification(message: str, subject: str, smtp_server: str, port: int, from_addr: str, to_addr: str, password: str):
    """
    Sends an email notification using SMTP.
    """
    email_msg = EmailMessage()
    email_msg.set_content(message)
    email_msg['Subject'] = subject
    email_msg['From'] = from_addr
    email_msg['To'] = to_addr

    try:
        with smtplib.SMTP_SSL(smtp_server, port) as server:
            server.login(from_addr, password)
            server.send_message(email_msg)
    except Exception as e:
        print(f"Error sending email: {e}")
