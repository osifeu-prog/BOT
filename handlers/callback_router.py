from callbacks.menu import menu_callback

async def handle_callback(callback: dict):
    data = callback.get("data", "")
    if data.startswith("menu_"):
        await menu_callback(callback)
