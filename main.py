import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers import start_command, handle_voice, handle_text, stats_command, list_command, help_command, admin_command
from scheduler import start_scheduler
from config import TELEGRAM_BOT_TOKEN
from messages import Messages

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("list", list_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("admin", admin_command))
    
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    start_scheduler()
    
    print(Messages.BOT_STARTED)
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
