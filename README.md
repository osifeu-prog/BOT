#  כל התיעוד
Set-Content -Path "README.md" -Value @'
# 🎰 NFTY PRO - Telegram Casino & Trading SaaS

![Status](https://img.shields.io/badge/Status-Live-success)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-Commercial-orange)

**NFTY PRO** is an enterprise-grade Telegram bot infrastructure designed for high-volume casino games, affiliate marketing, and crypto payments using the TON ecosystem.

---

## 🚀 Features

### 🎮 Game Engine
* **Mines:** Provably Fair logic with dynamic win rates based on user tiers
* **Anti-Cheat:** Server-side validation for every move
* **Tier System:** Free, Pro, and VIP levels with different game settings

### 💰 Monetization (SaaS)
* **Crypto Payments:** Native integration with **CryptoBot** (USDT/TON)
* **Tier System:** Managed via Redis with automatic upgrades
* **Affiliate System:** Multi-level referral tracking with auto-payout calculation
* **Shop System:** In-app purchases for boosts and upgrades

### 📊 CRM & Admin Dashboard
* **Real-time Analytics:** Visual graphs generated on-the-fly
* **User Management:** Ban, mute, and balance adjustments via commands
* **Broadcast System:** Mass messaging tool for marketing campaigns
* **Export System:** Excel exports of user data and transactions

---

📁 מבנה תיקיות סופי מלא
text
BOT/
├── admin/
│   ├── __init__.py
│   ├── dashboard.py
│   ├── exporter.py
│   └── tools.py
├── app/
│   ├── __init__.py
│   ├── auth/
│   │   ├── __init__.py
│   │   └── roles.py
│   ├── bot/
│   │   ├── __init__.py
│   │   └── welcome.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── affiliate.py
│   │   ├── payment_webhooks.py
│   │   ├── payments.py
│   │   └── shop.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── manager.py
│   ├── games/
│   │   ├── __init__.py
│   │   ├── crash.py
│   │   ├── mines.py
│   │   ├── slots.py
│   │   ├── roulette.py      # 🆕 חדש!
│   │   ├── blackjack.py     # 🆕 חדש!
│   │   └── dice.py          # 🆕 חדש!
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── helpers.py
│   │   ├── logger.py
│   │   ├── daily_tasks.py   # 🆕 חדש!
│   │   ├── leaderboard.py   # 🆕 חדש!
│   │   └── themes.py        # 🆕 חדש!
│   ├── security.py          # 🔄 משודרג!
│   └── templates.py
├── scripts/
│   ├── project_manager.ps1
│   ├── railway.setup.ps1    # ❗ לא צריך לעלות לגיט!
│   └── run_tests.ps1
├── .env.example
├── .gitattributes
├── .gitignore              # 🔄 מעודכן!
├── Main.py                 # 🔄 משודרג!
├── README.md
├── config.py
├── health.py
├── railway.json
└── requirements.txt        # 🔄 מעודכן!


## 🛠️ Installation

### Prerequisites
1. **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)
2. **Redis Database** (Railway or self-hosted)
3. **CryptoBot API Token** from [@CryptoBot](https://t.me/CryptoBot)
4. **Railway Account** for deployment

### Local Development
```bash
# Clone repository
git clone https://github.com/osifeu-prog/BOT.git
cd BOT

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run the bot
python Main.py
Railway Deployment
Connect your GitHub repository to Railway

Add environment variables in Railway dashboard

Deploy automatically on push

⚙️ Environment Variables
env
# Required
TELEGRAM_TOKEN=your_bot_token_here
REDIS_URL=redis://:password@host:port
ADMIN_ID=your_telegram_id

# Optional (with defaults)
REFERRAL_REWARD=500
WIN_CHANCE_PERCENT=80
CRYPTO_PAY_TOKEN=your_cryptobot_token
PARTICIPANTS_GROUP_LINK=https://t.me/your_group
📋 Available Commands
User Commands
/start - Start the bot and show main menu

Daily bonus from menu

Mine game from menu

Shop and upgrades from menu

Affiliate panel from menu

Admin Commands
/gift [user_id] [amount] - Gift balance to user

/broadcast [message] - Broadcast message to all users

🎮 Game: Mines
Tier Configuration
Tier	Mines	Multiplier	Features
Free	5	1.1x	Basic gameplay
Pro	3	1.3x	10% better odds
VIP	2	1.5x	30% better odds, no mines
How to Play
Click "Mines Game" in main menu

Click on cells to reveal diamonds

Avoid mines to win multiplier

Cash out anytime or risk losing

💼 Business Model
Revenue Streams
VIP Subscriptions ($50/$150 one-time)

Transaction Fees (5% on winnings)

Affiliate Commissions (20% from referrals)

Cost Structure
Server Costs (Railway: $5-20/month)

Payment Processing (CryptoBot: 1-2%)

Development & Maintenance

🚨 Security Features
Rate limiting on all commands

Server-side game validation

Redis persistence and backups

Admin-only access to sensitive commands

Encrypted environment variables

📈 Analytics & Reporting
Admin Dashboard Features
Real-time user count graph

Excel export of all user data

Transaction logging

Referral tracking

Revenue reporting

🔄 Update Log
Latest Changes
✅ Fixed Railway deployment issues

✅ Added Mines game with tier system

✅ Implemented Crypto payments

✅ Created admin dashboard

✅ Added affiliate system

✅ Fixed import errors and file structure

📞 Support & Contact
Developer: @osifeu-prog

Support Group: Join Here

Issues: GitHub Issues

Documentation: Read this README

📄 License
This project is proprietary software. All rights reserved.

© 2024 NFTY PRO. Not for public distribution.
'@

Write-Host "✅ README.md created successfully!" -ForegroundColor Green
