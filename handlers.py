import json
from openai import OpenAI
from telegram import Update
from telegram.ext import ContextTypes
from database import Database
from config import OPENAI_API_KEY, ADMIN_PASSWORD
from datetime import datetime
from scheduler import reschedule_job
from messages import Messages

client = OpenAI(api_key=OPENAI_API_KEY)
db = Database()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(Messages.START_MESSAGE)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    db.add_or_update_user(user.id, user.username, user.first_name)
    
    await update.message.chat.send_action("typing")
    
    try:
        voice_file = await update.message.voice.get_file()
        voice_path = f"voice_{user.id}.ogg"
        await voice_file.download_to_drive(voice_path)
        
        with open(voice_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="uk"
            )
        
        text = transcript.text
        
        await process_message(update, context, text)
        
        import os
        os.remove(voice_path)
        
    except Exception as e:
        await update.message.reply_text(
            Messages.ERROR_VOICE.format(error=str(e))
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    db.add_or_update_user(user.id, user.username, user.first_name)
    
    text = update.message.text
    await process_message(update, context, text)

async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    await update.message.chat.send_action("typing")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": Messages.PROMPT_CLASSIFIER
                },
                {"role": "user", "content": text}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        if result["type"] == "fact":
            await handle_fact(update, result)
        elif result["type"] == "question":
            await handle_question(update, result)
            
    except Exception as e:
        await update.message.reply_text(
            Messages.ERROR_GENERAL.format(error=str(e))
        )

async def handle_fact(update: Update, data: dict):
    user_id = update.message.from_user.id
    name = data["name"]
    content = data["content"]
    birthday = data.get("birthday")
    
    contact = db.get_contact(user_id, name)
    
    if contact:
        db.update_contact(contact["id"], content, birthday)
    else:
        db.add_contact(user_id, name, content, birthday)
    
    response = Messages.SAVED_SUCCESS.format(name=name)
    
    if birthday:
        birthday_date = datetime.strptime(birthday, "%Y-%m-%d")
        response += Messages.BIRTHDAY_ADDED.format(date=birthday_date.strftime('%d %B'))
    response += Messages.FORGOT_HELP
    await update.message.reply_text(response)

async def handle_question(update: Update, data: dict):
    user_id = update.message.from_user.id
    name = data["name"]
    
    contact = db.get_contact(user_id, name)
    
    if not contact:
        await update.message.reply_text(
            Messages.UNKNOWN_PERSON.format(name=name)
        )
        return
    
    await update.message.chat.send_action("typing")
    
    try:
        context_text = contact["context"]
        if contact["birthday"]:
            birthday_date = datetime.strptime(contact["birthday"], "%Y-%m-%d")
            context_text += f"\n\nДень народження: {birthday_date.strftime('%d %B')}"
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": Messages.PROMPT_ANSWER
                },
                {
                    "role": "user",
                    "content": f"Контекст про {name}:\n{context_text}\n\nПитання користувача: {data['content']}\n\nТвоя відповідь:"
                }
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        answer = response.choices[0].message.content
        await update.message.reply_text(answer + Messages.FORGOT_HELP)
        
    except Exception as e:
        await update.message.reply_text(
            Messages.ERROR_GENERATION.format(error=str(e))
        )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    contacts = db.get_all_contacts(user_id)
    
    total = len(contacts)
    with_birthdays = sum(1 for c in contacts if c["birthday"])
    
    await update.message.reply_text(
        Messages.STATS_TEMPLATE.format(total=total, with_birthdays=with_birthdays)
    )

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    contacts = db.get_all_contacts(user_id)
    
    if not contacts:
        await update.message.reply_text(Messages.LIST_EMPTY)
        return
    
    response = Messages.LIST_HEADER
    
    for contact in contacts:
        response += f"👤 {contact['name']}\n"
        if contact['birthday']:
            birthday_date = datetime.strptime(contact['birthday'], "%Y-%m-%d")
            response += f"   🎂 {birthday_date.strftime('%d %B')}\n"
        response += "\n"
    
    await update.message.reply_text(response)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        Messages.HELP_MESSAGE,
        parse_mode="Markdown"
    )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text(Messages.ADMIN_USAGE)
        return
    
    password = context.args[0]
    time_str = context.args[1]
    
    if password != ADMIN_PASSWORD:
        await update.message.reply_text(Messages.ADMIN_INVALID_PASS)
        return
    
    if reschedule_job(time_str):
        await update.message.reply_text(Messages.ADMIN_SUCCESS.format(time=time_str))
    else:
        await update.message.reply_text(Messages.ADMIN_ERROR)