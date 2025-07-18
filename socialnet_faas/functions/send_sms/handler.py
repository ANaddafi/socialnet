def handler(event, context=None):
    """
    Expects event to have: 'to', 'body'
    """
    to = event.get("to")
    body = event.get("body")
    if not to or not body:
        return {"statusCode": 400, "body": {"error": "Missing parameters"}}

    print(f"Send SMS to: {to} | body: {body}")

    # TODO: Actual sending logic

    return {"statusCode": 200, "body": {"status": "sent", "to": to}}
