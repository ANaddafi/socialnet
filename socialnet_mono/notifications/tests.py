import pytest
from unittest.mock import patch, MagicMock

from notifications.services.dispatcher import NotificationDispatcher


class DummyUser:
    def __init__(self, id, email, phone):
        self.id = id
        self.email = email
        self.phone = phone


@pytest.fixture
def user():
    return DummyUser(id=1, email="user@test.com", phone="+989123456789")


def test_notify_success_push_first(user):
    dispatcher = NotificationDispatcher()

    with patch("notifications.services.channels.push_channel.PushChannel.send") as mock_push, \
         patch("notifications.services.channels.email_channel.EmailChannel.send") as mock_email, \
         patch("notifications.services.channels.sms_channel.SMSChannel.send") as mock_sms:

        mock_push.return_value = {"status": "sent"}

        result = dispatcher.notify(user, "comment", "title", "body")

        assert result["status"] == "sent"
        assert mock_push.call_count == 1
        assert mock_email.call_count == 0
        assert mock_sms.call_count == 0


def test_notify_push_fail_email_success(user):
    dispatcher = NotificationDispatcher()

    with patch("notifications.services.channels.push_channel.PushChannel.send") as mock_push, \
         patch("notifications.services.channels.email_channel.EmailChannel.send") as mock_email, \
         patch("notifications.services.channels.sms_channel.SMSChannel.send") as mock_sms:

        mock_push.side_effect = Exception("Push down")
        mock_email.return_value = {"status": "sent"}

        result = dispatcher.notify(user, "comment", "title", "body")

        assert result["status"] == "sent"
        assert mock_push.call_count == 1
        assert mock_email.call_count == 1
        assert mock_sms.call_count == 0


def test_notify_all_fail(user):
    dispatcher = NotificationDispatcher()

    with patch("notifications.services.channels.push_channel.PushChannel.send", side_effect=Exception("Push fail")), \
         patch("notifications.services.channels.email_channel.EmailChannel.send", side_effect=Exception("Email fail")), \
         patch("notifications.services.channels.sms_channel.SMSChannel.send", side_effect=Exception("SMS fail")):

        with pytest.raises(Exception, match="All notification channels failed"):
            dispatcher.notify(user, "comment", "title", "body")
