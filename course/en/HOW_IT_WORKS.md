# 🧠 How the bot works internally

In this lesson you'll understand the full flow of the system – from the Telegram user to the database.

--- PAGE ---

## High-level data flow

Basic flow:

1. User sends a message / taps a button in Telegram.
2. Telegram sends an Update to your webhook.
3. FastAPI receives the request at `/webhook`.
4. We check if it's a `message` or `callback_query`.
5. We route it to the appropriate handlers.
6. We log events in the DB.
7. We respond to the user via the Telegram API.

--- PAGE ---

## main.py – entry point

In `main.py`:

- We create a `FastAPI()` app.
- We define:
  - `GET /` – health check.
  - `POST /webhook` – entry point for Telegram updates.

From there we call `handle_message` or `handle_callback`.

--- PAGE ---

## handlers/router.py – text messages

In `handle_message`:

- We extract:
  - `user_id`
  - `text`
  - `language_code`
- Detect language (`he` / `en`).
- Log an event in `user_events`.
- If `/start` – send main menu.
- If `/admin` – route to `admin_handler`.

This is the main gateway for text messages.

--- PAGE ---

## handlers/callback_router.py – inline buttons

In `handle_callback`:

- We read `callback["data"]`.
- If it starts with `menu_` – route to `menu_callback`.
- If it starts with `course|` – route to `course_callback`.

This keeps menu logic and course logic separated.

--- PAGE ---

## db/events.py – event log

Every important user action is stored in `user_events`:

- `event_type` – e.g. `message`, `button`
- `data` – message text / callback data
- `created_at` – timestamp

This enables:

- Statistics
- Behavior analysis
- Debugging

--- PAGE ---

## edu_log – educational logs

Throughout the code we call:

- `edu_step(...)`
- `edu_path(...)`
- `edu_warning(...)`

When `DEBUG_MODE=true`, you'll see in Railway logs:

- Which path was triggered
- Which step is running
- Where errors occur

This turns the code into a learning tool, not just a black box.

--- PAGE ---

## Summary

Your bot is essentially:

- A small API (FastAPI)
- Talking to:
  - Telegram
  - Database
  - Redis
- Managing:
  - A course
  - Payments
  - A game
  - An admin panel

In the next lessons we'll dive into each part.
