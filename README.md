# 🖥️ Personal Dashboard

A personal dashboard with a Flask web interface and a Telegram bot for task management and server monitoring.

## Features

- 📋 Task management (create, update, delete)
- ⏰ Telegram reminders when tasks are due
- 📊 Server status monitoring (CPU, RAM, disk)
- 🔐 Login-protected web interface

## Requirements

- Python 3.9+
- Docker & Docker Compose
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Your Telegram User ID (from [@userinfobot](https://t.me/userinfobot))

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Andreagod/personal_dashboard.git
cd personal_dashboard
```

### 2. Create a user account

Create a virtual environment, install dependencies, and run the user creation script:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python scripts/create_user.py
```

Follow the prompts to set your username and password, then deactivate the venv:

```bash
deactivate
```

### 3. Configure the environment

Open the `.env` file and fill in your Telegram credentials:

```bash
nano .env
```

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_ADMIN_ID=your_telegram_user_id_here
```

### 4. Start the application

```bash
sudo docker compose up --build
```

The dashboard will be available at `http://localhost:5000`

---

## Usage

- Open `http://your-server-ip:5000` in your browser
- Log in with the credentials you created in step 2
- Use the Telegram bot commands:
  - `/start` — Start the bot
  - `/tasks` — View your pending tasks

The bot will automatically send you a Telegram message when a task is due.

---

## Project Structure

```
personal_dashboard/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   └── templates/
├── scripts/
│   └── create_user.py
├── bot.py
├── config.py
├── run.py
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```
