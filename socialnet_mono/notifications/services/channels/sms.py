import requests

from .base import NotificationChannel


class SMSChannel(NotificationChannel):
    def send(self, user, title, body, **kwargs):
        payload = {
            "to": user.phone,
            "body": body,
        }
        response = requests.post("http://faas.example.com/send_sms", json=payload)
        response.raise_for_status()
        return response.json()
