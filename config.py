import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

REMINDER_TIME = "13:20"
REMINDER_DAYS_AHEAD = 40
TIMEZONE = "Europe/Warsaw"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "1234567")
