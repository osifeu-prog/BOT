# 📂 Full code explained – complete guide

In this lesson we'll walk through all the main files in the system and explain what each part does.

--- PAGE ---

## main.py

- Creates FastAPI app
- Defines:
  - `GET /` – health check
  - `POST /webhook` – entry point for Telegram updates
- Calls:
  - `handle_message` for `message`
  - `handle_callback` for `callback_query`

This is the main gateway between Telegram and your code.

--- PAGE ---

## utils/config.py

- Reads environment variables:
  - Bot token
  - Webhook URL
  - DB connection
  - Redis connection
  - Prices
  - Payment details
- Defines your contact details (phone, email, Telegram)

This lets you change settings without touching code.

--- PAGE ---

## utils/telegram.py

- `send_message` – sends text messages
- `send_document` – sends documents (or file URLs)

A simple wrapper around Telegram Bot API so you don't repeat `requests.post` everywhere.

--- PAGE ---

## utils/i18n.py

- `detect_language_from_telegram` – returns `he` or `en`
- `t(lang, he, en)` – chooses text based on language

This keeps bilingual text clean and readable.

--- PAGE ---

## utils/edu_log.py

- `edu_step` – prints numbered steps
- `edu_path` – prints flow paths
- `edu_warning` / `edu_error` – prints warnings and errors

When `DEBUG_MODE=true`, you'll see all of this in the logs.

--- PAGE ---

## db/connection.py

- Creates a Postgres connection using `DATABASE_URL`.

Other DB files use it to avoid duplicating connection logic.

--- PAGE ---

## db/admins.py, db/buyers.py

- `admins.py` – who is an admin
- `buyers.py` – who purchased

Functions:

- `_ensure_table` – creates table if missing
- `is_admin` / `is_buyer`
- `add_admin` / `add_buyer`

--- PAGE ---

## db/events.py

- `user_events` table:
  - `user_id`
  - `event_type`
  - `data`
  - `created_at`

Function:

- `log_event` – inserts a new event.

--- PAGE ---

## db/slots.py, db/stats.py, db/course_progress.py

- `slots.py` – SLOTS game history
- `stats.py` – basic stats (users, buyers, events)
- `course_progress.py` – course progress (Redis)

Each focuses on a specific table/domain.

--- PAGE ---

## handlers/router.py

- Handles text messages.
- Detects:
  - `/start`
  - `/admin`
- Sends main menu or routes to `admin_handler`.

--- PAGE ---

## handlers/callback_router.py

- Handles `callback_query`.
- If `data` starts with `menu_` – routes to `menu_callback`.
- If `data` starts with `course|` – routes to `course_callback`.

--- PAGE ---

## handlers/admin.py

- `/admin <password>` – makes a user admin.
- `/grant <user_id>` – grants course access.
- `/astats` – basic stats.
- `/alogs` – recent events.
- `/export buyers` / `/export events` – CSV export (basic logic).

--- PAGE ---

## handlers/slots.py

- `play_slots` – runs a single game.
- `show_leaderboard` – shows leaderboard.

Uses `WIN_CHANCE_PERCENT` to control win probability.

--- PAGE ---

## callbacks/menu.py

- Handles all `menu_*` buttons.
- Includes:
  - Purchase
  - Course
  - How it works
  - Telegram UI
  - Game
  - Leaderboard
  - Support

--- PAGE ---

## callbacks/course.py

- `LESSON_FILES` – maps lessons to Markdown files.
- `send_lesson_page` – shows a specific page:
  - Demo mode
  - Buyer/admin check
  - Progress saving
- `course_callback` – parses `course|LESSON_KEY|PAGE_INDEX`.

--- PAGE ---

## buttons/menus.py

- `get_main_menu` – main menu.
- `get_course_menu` – course lessons menu.

Each button has `callback_data` that connects to logic.

--- PAGE ---

## texts/*.py

- `payment.py` – payment texts.
- `how_it_works.py` – short explanation of how the bot works.
- `telegram_ui.py` – short explanation of Telegram UI.

Bilingual texts for quick use.

--- PAGE ---

## course/*.md

- Each lesson in the course.
- Split into pages with `--- PAGE ---`.
- Includes:
  - Explanations
  - Examples
  - Assignments

The bot displays them based on user interaction.

--- PAGE ---

## landing/

- `index.html` – landing page.
- `style.css` – styling.

You can extend it with forms, video, testimonials, etc.

--- PAGE ---

## Summary

You now have:

- Full code
- Full course
- Explanations for every part
- A template for future bots and products

From here – it's yours: to play, change, sell, and teach.
