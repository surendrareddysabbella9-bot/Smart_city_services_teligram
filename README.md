# Smart City Services Telegram Bot

A Telegram bot that connects users with city service workers (Electricians, Plumbers, Construction Workers).

## Features

- 🚀 Simple service selection via inline buttons
- 📍 Location-based worker requests
- ⚡ Asynchronous handlers for concurrent users
- 📝 Clear logging for debugging

## Prerequisites

- Python 3.10 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

## Setup

### 1. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy the example env file
copy .env.example .env   # Windows
cp .env.example .env     # Linux/macOS

# Edit .env and add your bot token
BOT_TOKEN=your_telegram_bot_token_here
```

### 4. Run the Bot

```bash
python bot.py
```

## Usage

1. Open Telegram and search for your bot
2. Send `/start` to begin
3. Select a service (Electrician, Plumber, or Construction Worker)
4. Enter your area/location
5. Receive confirmation that nearby workers will be notified

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and view services |
| `/cancel` | Cancel the current request |

## Project Structure

```
telegram-bot/
├── bot.py           # Main bot script
├── requirements.txt # Python dependencies
├── .env             # Environment variables (not in git)
├── .env.example     # Environment template
├── .gitignore       # Git ignore rules
└── README.md        # This file
```

## 🚀 Deploy to Railway (Free - Always Running)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/telegram-bot.git
git push -u origin main
```

### Step 2: Deploy on Railway
1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your `telegram-bot` repository
4. Click **"Add Variables"** and add:
   - `BOT_TOKEN` = your Telegram bot token
5. Railway will auto-deploy and your bot runs 24/7! 🎉

### Step 3: Verify
- Check the **Deployments** tab for logs
- Your bot should show "Bot started successfully!"

## License

MIT
