from .channels.email import EmailChannel
from .channels.sms import SMSChannel
from .channels.push import PushChannel


class NotificationDispatcher:
    def __init__(self):
        self.channels = {
            "email": EmailChannel(),
            "sms": SMSChannel(),
            "push": PushChannel(),
        }

    def notify(self, user, event_type, title, body, **kwargs):
        preferences = self.get_user_preferences(user, event_type)
        for channel_name in preferences:
            channel = self.channels.get(channel_name)
            if channel:
                try:
                    result = channel.send(user, title, body, **kwargs)
                    # TODO: Log success, break after first successful send
                    return result
                except Exception as e:
                    # TODO: Log error, try next channel
                    continue
        # TODO: If all channels fail, log failure
        raise Exception("All notification channels failed")

    def get_user_preferences(self, user, event_type):
        # Query DB or hardcode for demo
        # Example: user prefers push for comments, email for others
        if event_type == "comment":
            return ["push", "email", "sms"]
        else:
            return ["email", "push", "sms"]
