import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Код сам заберет ваши токены из скрытых настроек Render!
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
SMART_KEY = os.getenv("SMART_API_KEY") 
ALLOWED_IDS = [id.strip() for id in os.getenv("ALLOWED_USER_ID", "").split(",") if id.strip()]

# ОСТАВЛЯЕМ СТРОГО ВАШ ВАРИАНТ:
BASE_URL = "https://api.smartapi.shop" 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_IDS:
        return
    await update.message.reply_text("Привет! Я ваш личный ИИ-ассистент в чате!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    bot_username = context.bot.username

    if user_id not in ALLOWED_IDS:
        return

    if update.effective_chat.type in ["group", "supergroup"]:
        is_mentioned = update.message.text and f"@{bot_username}" in update.message.text
        is_reply_to_bot = update.message.reply_to_message and update.message.reply_to_message.from_user.username == bot_username
        if not (is_mentioned or is_reply_to_bot):
            return 

    user_text = update.message.text.replace(f"@{bot_username}", "").strip()
    if not user_text:
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # Автоматически склеиваем ваш BASE_URL со стандартным путем для ИИ-чата
    full_url = f"{BASE_URL.rstrip('/')}/v1/chat/completions"

    response = requests.post(
        url=full_url,
        headers={
            "Authorization": f"Bearer {SMART_KEY}",
            "Content-Type": "application/json",
        },
        json={
            # При необходимости замените gpt-4o на ту модель, которая активна на вашем балансе
            "model": "claude-opus-5", 
            "messages": [{"role": "user", "content": user_text}]
        }
    )

    try:
        reply = response.json()['choices']['message']['content']
    except Exception:
        reply = f"Ошибка шлюза. Проверьте модель/баланс. Ответ сервера:\n{response.text[:200]}"

    await update.message.reply_text(reply, reply_to_message_id=update.message.message_id)

def main():
    app = Application.builder().token(TG_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
