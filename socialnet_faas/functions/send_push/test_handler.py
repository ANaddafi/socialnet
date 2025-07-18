from .handler import handler


def test_push_success():
    event = {"user_id": 42, "title": "Alert", "body": "Check your messages"}
    context = {}
    result = handler(event, context)
    assert result["statusCode"] == 200
    assert result["body"]["status"] == "sent"
    assert result["body"]["user_id"] == 42


def test_push_missing_params():
    event = {"user_id": 42, "title": "Alert"}
    context = {}
    result = handler(event, context)
    assert result["statusCode"] == 400
    assert "error" in result["body"]
