# 🎛 Telegram UI – all the options

In this lesson you'll learn about the different UI elements a bot can use in Telegram, and how they connect to your code.

--- PAGE ---

## Reply Keyboard

Reply Keyboard replaces the user's normal keyboard.

Characteristics:

- Stays open until replaced
- Good for simple flows
- Harder to track (no callback_data)

In this course we focus more on Inline Keyboard, but it's important to know.

--- PAGE ---

## Inline Keyboard

Inline Keyboard appears under a message.

Characteristics:

- Each button sends a `callback_query`
- Has `callback_data` – a short string sent to the bot
- Enables complex logic (menus, courses, games)

In our code:

- `buttons/menus.py` builds the inline keyboards
- `handlers/callback_router.py` routes based on `callback_data`

--- PAGE ---

## Bot Commands

Commands like `/start`, `/admin`, `/help`.

- Configured in BotFather
- Shown to the user in the command menu
- In code, we check `text.startswith("/start")`, etc.

Commands are a good entry point for different flows.

--- PAGE ---

## Bot Menu

Telegram allows a persistent "Bot Menu":

- A list of buttons always available to the user
- Configured via BotFather
- Example: "Start", "Help", "Buy"

We don't configure it in code here, but you can add it later.

--- PAGE ---

## WebApps

WebApps open a web view inside Telegram:

- For complex forms, dashboards, shops
- Requires frontend (HTML/JS)
- The bot receives data from the WebApp

This is more advanced – you can add it as a future module.

--- PAGE ---

## Attachment Menu

Bots can appear in the attachment menu:

- Lets users pick the bot from the "paperclip" menu
- Useful for bots that work with files/images

Less relevant for this course, but good to know.

--- PAGE ---

## How it connects to our course

In this course:

- We mainly use Inline Keyboards
- Each button represents:
  - A menu
  - A lesson
  - A page in the course
  - A game

Understanding Telegram UI helps you design better user experiences.
