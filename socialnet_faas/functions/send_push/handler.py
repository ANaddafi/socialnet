def handler(event, context=None):
    """
    Expects event to have: 'user_id', 'title', 'body'
    """
    user_id = event.get("user_id")
    title = event.get("title")
    body = event.get("body")
    if not user_id or not title or not body:
        return {"statusCode": 400, "body": {"error": "Missing parameters"}}

    print(f"Send PUSH to user_id: {user_id} | title: {title} | body: {body}")

    # TODO: Actual sending logic

    return {"statusCode": 200, "body": {"status": "sent", "user_id": user_id}}
