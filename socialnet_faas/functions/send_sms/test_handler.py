from .handler import handler


def test_sms_success():
    event = {"to": "+989123456789", "body": "Hello!"}
    context = {}
    result = handler(event, context)
    assert result["statusCode"] == 200
    assert result["body"]["status"] == "sent"
    assert result["body"]["to"] == "+989123456789"


def test_sms_missing_params():
    event = {"to": "+989123456789"}
    context = {}
    result = handler(event, context)
    assert result["statusCode"] == 400
    assert "error" in result["body"]
