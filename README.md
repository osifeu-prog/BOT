
# FreePlay Platform MVP

## Overview
Free-to-play gamified Telegram + Web platform.
No real money, points only.

## Features
- Free games (slots demo)
- Points-based rewards
- Shop (access & roles)
- Admin roles
- Telegram webhook ready
- Railway-ready deployment

## Environment Variables
- ADMIN_USERNAME
- ADMIN_PASSWORD
- TELEGRAM_TOKEN
- WEBHOOK_URL
- PORT=8080

## Deployment (Railway)
1. Upload ZIP or push to GitHub
2. Create Railway project
3. Add environment variables
4. Deploy
5. Verify `/health` returns OK

## Testing Checklist
- `/health` -> OK
- `/games/slots` returns result
- `/shop/items` returns items
- Admin login works
- Railway logs show no errors
