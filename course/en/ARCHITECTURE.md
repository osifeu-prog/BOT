# 🏗 System architecture

In this lesson you'll see how all folders and files connect into one coherent system.

--- PAGE ---

## Folder structure

High-level structure:

- `main.py` – entry point
- `handlers/` – message and callback handling
- `callbacks/` – menu and course logic
- `buttons/` – building menus
- `utils/` – shared utilities (config, logs, Telegram, i18n)
- `db/` – database access
- `texts/` – static bilingual texts
- `course/` – course content (Markdown)
- `landing/` – landing page

--- PAGE ---

## main.py – API heart

- Creates FastAPI app
- Defines `/` and `/webhook`
- Contains no business logic – only routing

This keeps the code clean and easy to reason about.

--- PAGE ---

## handlers/ – logical routing layer

- `router.py` – text messages
- `callback_router.py` – inline buttons
- `admin.py` – admin logic
- `slots.py` – SLOTS game

Each handler is responsible for a clear domain.

--- PAGE ---

## callbacks/ – menu and course logic

- `menu.py` – main menu, payments, game, support
- `course.py` – lessons, demo mode, progress

This is where "what happens when a user taps a button" is defined.

--- PAGE ---

## db/ – data access layer

- `connection.py` – Postgres connection
- `admins.py` – admins table
- `buyers.py` – buyers table
- `events.py` – event log
- `slots.py` – game history
- `course_progress.py` – course progress (Redis)
- `stats.py` – admin stats

Goal: keep all DB access in one place.

--- PAGE ---

## utils/ – shared utilities

- `config.py` – environment variables
- `telegram.py` – sending messages/documents
- `i18n.py` – language handling
- `edu_log.py` – educational logs
- `content.py` – reading Markdown files

This keeps the code DRY and modular.

--- PAGE ---

## course/ – content layer

- `course/he/*.md` – Hebrew course
- `course/en/*.md` – English course
- Each file is split into pages using `--- PAGE ---`

The bot doesn't "know" the content – it just serves it.

--- PAGE ---

## landing/ – landing page

- `index.html` – structure
- `style.css` – styling

You can host it on Netlify / Vercel / GitHub Pages or any static hosting.

--- PAGE ---

## Summary

The architecture is designed so you can:

- Understand each layer separately
- Swap components (DB, landing page, etc.)
- Extend the system (more games, more courses, more payment flows)

This is not just a bot – it's a template for future digital products.
