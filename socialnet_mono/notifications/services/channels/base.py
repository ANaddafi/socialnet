from abc import ABC, abstractmethod


class NotificationChannel(ABC):
    @abstractmethod
    def send(self, user, title, body, **kwargs):
        """Send notification via specific channel"""
        pass
