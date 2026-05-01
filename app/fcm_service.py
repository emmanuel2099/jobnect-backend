"""
Firebase Cloud Messaging (FCM) Service
Sends push notifications to mobile devices
"""
import os
import json
import time
import requests
from typing import List, Optional, Dict
from google.oauth2 import service_account
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]
PROJECT_ID = "eagelpride"
FCM_URL = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "..", "firebase-service-account.json")


def _get_access_token() -> str:
    """Get OAuth2 access token from service account credentials."""
    # Try env variable first (for production), then fall back to file
    sa_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if sa_json:
        import json
        from google.oauth2.service_account import Credentials
        info = json.loads(sa_json)
        credentials = Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
    credentials.refresh(Request())
    return credentials.token


def send_notification_to_token(
    fcm_token: str,
    title: str,
    body: str,
    data: Optional[Dict] = None
) -> bool:
    """Send push notification to a single device token."""
    try:
        access_token = _get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        message = {
            "message": {
                "token": fcm_token,
                "notification": {"title": title, "body": body},
                "android": {
                    "notification": {
                        "sound": "default",
                        "click_action": "FLUTTER_NOTIFICATION_CLICK"
                    }
                },
                "data": {k: str(v) for k, v in (data or {}).items()}
            }
        }
        response = requests.post(FCM_URL, headers=headers, json=message, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"FCM send error: {e}")
        return False


def send_notification_to_multiple(
    fcm_tokens: List[str],
    title: str,
    body: str,
    data: Optional[Dict] = None
) -> int:
    """Send push notification to multiple device tokens. Returns success count."""
    success = 0
    for token in fcm_tokens:
        if send_notification_to_token(token, title, body, data):
            success += 1
    return success


def send_job_alert_to_all(
    db,
    job_title: str,
    company_name: str,
    job_id: int,
    location: str = ""
) -> int:
    """Send job alert notification to all job seekers with FCM tokens."""
    from app.models import JobSeeker
    from sqlalchemy import and_

    job_seekers = db.query(JobSeeker).filter(
        JobSeeker.fcm_token != None,
        JobSeeker.fcm_token != ""
    ).all()

    tokens = [js.fcm_token for js in job_seekers if js.fcm_token]
    if not tokens:
        return 0

    title = "New Job Alert!"
    body = f"{job_title} at {company_name}"
    if location:
        body += f" • {location}"

    data = {"job_id": str(job_id), "type": "job_alert"}
    return send_notification_to_multiple(tokens, title, body, data)


def send_application_notification(
    fcm_token: str,
    status: str,
    job_title: str,
    company_name: str,
    application_id: int
) -> bool:
    """Notify job seeker about application status update."""
    status_messages = {
        "accepted": ("Application Accepted!", f"Congratulations! {company_name} accepted your application for {job_title}"),
        "rejected": ("Application Update", f"Your application for {job_title} at {company_name} was not selected"),
        "pending": ("Application Received", f"{company_name} received your application for {job_title}"),
        "interview": ("Interview Invitation!", f"{company_name} wants to interview you for {job_title}"),
    }
    title, body = status_messages.get(status, ("Application Update", f"Update on your {job_title} application"))
    data = {"application_id": str(application_id), "type": "application_update", "status": status}
    return send_notification_to_token(fcm_token, title, body, data)


def send_subscription_notification(fcm_token: str, plan_name: str) -> bool:
    """Notify user that subscription was activated."""
    return send_notification_to_token(
        fcm_token,
        "Subscription Activated!",
        f"Your {plan_name} subscription is now active. Start applying to jobs!",
        {"type": "subscription_activated"}
    )
