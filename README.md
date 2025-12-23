# 🧠 Memory Bot

**Memory Bot** is a smart personal assistant for Telegram that helps you remember important facts about people and never miss a birthday. It uses OpenAI's GPT-4o and Whisper models to understand text and voice messages, store information, and provide intelligent reminders.

## ✨ Features

- **📝 Fact Storage**: Simply tell the bot facts about people (e.g., "Ivan loves craft beer", "Mom's birthday is May 10th").
- **🎤 Voice Support**: Send voice messages, and the bot will transcribe and process them automatically.
- **❓ Smart Q&A**: Ask questions like "What should I get Ivan?" or "When is Mom's birthday?" and get instant answers.
- **🎂 Birthday Reminders**: The bot automatically checks for upcoming birthdays and sends you a reminder 7 days in advance with gift ideas based on stored facts.
- **🇺🇦 Ukrainian Localization**: Fully localized interface and prompts in Ukrainian.

## 🚀 Installation

### Prerequisites

- Python 3.9+
- Docker & Docker Compose (optional, for easy deployment)
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- OpenAI API Key

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/memory-bot.git
   cd memory-bot
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```
   Edit `.env`:
   ```ini
   TELEGRAM_BOT_TOKEN=your_token_here
   OPENAI_API_KEY=your_key_here
   ADMIN_PASSWORD=your_password_here
   ```

5. **Run the bot:**
   ```bash
   python main.py
   ```

### Docker Setup

1. **Configure `.env` as above.**

2. **Build and run:**
   ```bash
   docker-compose up --build -d
   ```

## 🛠 Commands

- `/start` - Start the bot and see instructions.
- `/stats` - View database statistics.
- `/list` - List all saved contacts.
- `/help` - Show help message.
- `/admin <password> <HH:MM>` - Restart the scheduler (Admin only).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
