async def handler(event):
    name = event.get("name", "world")
    return f"Hello, {name}!"
