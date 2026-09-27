import os
import base64
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES= ["https://www.googleapis.com/auth/gmail.send"]

def get_gmail_service():
    creds=None

    if os.path.exists("token.json"):
        creds=Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow=InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds=flow.run_local_server(port=0)
        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

def send_alert_email(to_address: str, subject: str, body: str):
    service=get_gmail_service()

    message=MIMEText(body)
    message["to"]=to_address
    message["subject"]=subject

    raw_message=base64.urlsafe_b64encode(message.as_bytes()).decode()

    service.users().messages().send(
        userId="me",
        body={"raw": raw_message}
    ).execute()

    print(f"Email sent to {to_address}")

if __name__=="__main__":
    send_alert_email(
        to_address="hananhidayathulla3@gmail.com",
        subject="Test - Anomaly Detector",
        body="This is a test email from the anomaly detector agent."
    )