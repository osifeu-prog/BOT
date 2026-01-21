# 🤖 Template for a new bot

In this lesson you'll learn how to turn this system into a template for future bots.

--- PAGE ---

## Why a template?

Once you have:

- main.py
- handlers
- callbacks
- utils
- db

You can:

- Spin up new bots quickly
- Reuse logic
- Only change what you need

This is the difference between a "one-off project" and a "platform".

--- PAGE ---

## What stays the same?

In every new bot:

- `main.py` – almost identical
- `utils/config.py` – similar (different env vars)
- `utils/telegram.py` – same idea
- `edu_log` – same idea
- `db/connection.py` – same idea

The foundation remains.

--- PAGE ---

## What changes?

Depending on the bot:

- `handlers/router.py` – message logic
- `callbacks/menu.py` – menus
- `course/` – if there's a course
- `texts/` – copy
- `landing/` – landing page

You can start from this template and remove what you don't need.

--- PAGE ---

## How to start a new bot?

1. Create a new project folder.
2. Copy the structure:
   - `main.py`
   - `handlers/`
   - `callbacks/`
   - `utils/`
   - `db/`
3. Remove unused parts (e.g. SLOTS if no game).
4. Update texts and menus.

--- PAGE ---

## Documentation for students/clients

If you sell bots:

- You can give them a course like this
- Teach them how to maintain the bot
- Show them where to change texts

This makes you a "developer + educator" – higher value.

--- PAGE ---

## Assignment

- Imagine a new bot (e.g. appointment booking bot).
- Write down:
  - Which parts of the template you keep?
  - Which parts you remove?
  - Which parts you add?

This trains you to think like a platform builder, not just a project coder.
