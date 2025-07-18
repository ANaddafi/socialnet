import requests

from .base import NotificationChannel


class PushChannel(NotificationChannel):
    def send(self, user, title, body, **kwargs):
        payload = {
            "user_id": user.id,
            "title": title,
            "body": body,
        }
        response = requests.post("http://faas.example.com/send_push", json=payload)
        response.raise_for_status()
        return response.json()
