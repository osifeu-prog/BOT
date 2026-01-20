def main_menu_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "לחץ כאן", "callback_data": "button_pressed"}
            ],
            [
                {"text": "בדיקת Redis", "callback_data": "test_redis"}
            ],
            [
                {"text": "בדיקת PostgreSQL", "callback_data": "test_postgres"}
            ],
            [
                {"text": "📘 שיעור: Redis & PostgreSQL", "callback_data": "lesson_db"}
            ]
        ]
    }
