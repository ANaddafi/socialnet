import requests

from .base import NotificationChannel


class EmailChannel(NotificationChannel):
    def send(self, user, title, body, **kwargs):
        # Example: call FaaS email endpoint
        payload = {
            "to": user.email,
            "subject": title,
            "body": body,
        }
        # Note: endpoint should be secured!
        response = requests.post("http://faas.example.com/send_email", json=payload)
        response.raise_for_status()
        return response.json()
