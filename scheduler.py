from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
from database import Database
from config import TELEGRAM_BOT_TOKEN, REMINDER_TIME, REMINDER_DAYS_AHEAD, TIMEZONE
from openai import OpenAI
from config import OPENAI_API_KEY
from messages import Messages
import pytz

bot = Bot(token=TELEGRAM_BOT_TOKEN)
db = Database()
client = OpenAI(api_key=OPENAI_API_KEY)

async def send_birthday_reminders():
    print(f"[{REMINDER_TIME}] {Messages.SCHEDULER_CHECKING}")
    
    upcoming = db.get_upcoming_birthdays(REMINDER_DAYS_AHEAD)
    
    for person in upcoming:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": Messages.PROMPT_REMINDER
                    },
                    {
                        "role": "user",
                        "content": Messages.SCHEDULER_PROMPT_USER.format(
                            days=person['days_until'],
                            name=person['name'],
                            context=person['context']
                        )
                    }
                ],
                temperature=0.8,
                max_tokens=250
            )
            
            reminder = response.choices[0].message.content
            
            await bot.send_message(
                chat_id=person["telegram_id"],
                text=Messages.REMINDER_HEADER.format(text=reminder)
            )
            
            print(Messages.SCHEDULER_SENT.format(id=person['telegram_id'], name=person['name']))
            
        except Exception as e:
            print(Messages.SCHEDULER_SEND_ERROR.format(error=e))

scheduler = AsyncIOScheduler(timezone=pytz.timezone(TIMEZONE))

def start_scheduler():
    hour, minute = map(int, REMINDER_TIME.split(":"))
    
    scheduler.add_job(
        send_birthday_reminders,
        'cron',
        hour=hour,
        minute=minute
    )
    
    scheduler.start()
    print(Messages.SCHEDULER_START.format(timezone=TIMEZONE, time=REMINDER_TIME))

def reschedule_job(new_time: str):
    try:
        hour, minute = map(int, new_time.split(":"))
        
        scheduler.remove_all_jobs()
        
        scheduler.add_job(
            send_birthday_reminders,
            'cron',
            hour=hour,
            minute=minute
        )
        
        print(Messages.SCHEDULER_RESTART.format(time=new_time, timezone=TIMEZONE))
        return True
    except Exception as e:
        print(Messages.SCHEDULER_ERROR.format(error=str(e)))
        return False
