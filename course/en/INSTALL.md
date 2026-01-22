# 📘 Installing the system on Railway

Welcome to the installation lesson. Here you'll learn how to deploy the bot, course and full system on Railway – step by step.

--- PAGE ---

## What is Railway and why use it?

Railway lets you:

- Deploy your code (like this bot)
- Attach a database (Postgres)
- Configure environment variables
- Get a public URL (for the webhook)

Instead of managing servers yourself – Railway does it for you.

--- PAGE ---

## Creating a new project on Railway

1. Go to https://railway.app
2. Sign in with GitHub / Google.
3. Click **New Project**.
4. Choose:
   - "Deploy from GitHub" if your code is in a repo
   - or "Empty Project" and deploy manually.

Goal: have an environment where your bot runs 24/7.

--- PAGE ---

## Adding a service for the bot

Inside your project:

1. Click **New Service**.
2. If using GitHub:
   - Select the repo with your bot code.
3. If deploying manually:
   - Use Railway CLI or upload via ZIP.

Railway will try to run your app based on your configuration.

--- PAGE ---

## Environment Variables

Go to **Variables** and set:

- `TELEGRAM_TOKEN` – token from BotFather
- `WEBHOOK_URL` – your webhook URL (e.g. `https://your-app.up.railway.app/webhook`)
- `DATABASE_URL` – Postgres connection string
- `REDIS_URL` – Redis connection (optional but recommended)
- `DEBUG_MODE` – `true` to see educational logs

For the full system:

- `PRICE_SH`, `LESSON_DB_PRICE`, `PEEK_COST`, `REFERRAL_REWARD`
- `CRYPTO_PAY_TOKEN`, `TON_WALLET`
- `PARTICIPANTS_GROUP_LINK`, `TEST_GROUP_LINK`

--- PAGE ---

## Creating a Postgres database

1. In your Railway project, click **New** → **Database**.
2. Choose Postgres.
3. Railway will generate a `DATABASE_URL`.
4. Copy it into your bot service variables.

Our code uses `DATABASE_URL` to connect to the DB.

--- PAGE ---

## Setting the webhook in BotFather

1. Open BotFather in Telegram.
2. Send `/setwebhook`.
3. Choose your bot.
4. Paste the `WEBHOOK_URL` you set in Railway.

If everything is correct – sending `/start` to your bot should work.

--- PAGE ---

## Sanity checks

Verify:

1. The `/` endpoint on Railway returns JSON with `"status": "Bot is running"`.
2. `/start` in Telegram works.
3. No critical errors in Railway logs.

If there are errors – read the logs and look for:
- ModuleNotFoundError
- ImportError
- DB connection issues

Debugging is part of becoming a real builder.
