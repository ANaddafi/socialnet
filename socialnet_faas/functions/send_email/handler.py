import os


def handler(event, context=None):
    """
    Expects event to have: 'to', 'subject', 'body'
    """
    to = event.get("to")
    subject = event.get("subject")
    body = event.get("body")
    if not to or not subject or not body:
        return {"statusCode": 400, "body": {"error": "Missing parameters"}}

    print(f"Send EMAIL to: {to} | subject: {subject} | body: {body}")

    # TODO: Actual sending logic

    return {"statusCode": 200, "body": {"status": "sent", "to": to}}