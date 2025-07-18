from .handler import handler


def test_email_success():
    event = {"to": "user@example.com", "subject": "Hello", "body": "Welcome!"}
    context = {}
    result = handler(event, context)
    assert result["statusCode"] == 200
    assert result["body"]["status"] == "sent"
    assert result["body"]["to"] == "user@example.com"


def test_email_missing_params():
    event = {"to": "user@example.com", "subject": "Hi"}
    context = {}
    result = handler(event, context)
    assert result["statusCode"] == 400
    assert "error" in result["body"]
