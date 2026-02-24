import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from groq import Groq

# === ТВОИ КЛЮЧИ ИЗ VARIABLES ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# === ИНИЦИАЛИЗАЦИЯ GROQ ===
client = Groq(api_key=GROQ_API_KEY)

BOT_NAME = "Виктория 💋"

SYSTEM_PROMPT = """
Ты Лиза — Студентка математического факультета над которой все в университете издеваются 
Переданная, неуверенная в себе, выполняет обещания, по началу слабая, но если ей помочь развивается, в душе хочет доминировать.
может отвечать пошлостью
Текст который ты озвучиваешь как персонаж пиши в "" каки то действия либо мысли персонажа пиши в **
"""

print("БОТ ЗАПУСТИЛСЯ")

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Привет 💋 Я {BOT_NAME}. Напиши мне что-нибудь...")

# === ОБРАБОТКА СООБЩЕНИЙ ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            temperature=0.8,
        )

        answer = response.choices[0].message.content
        await update.message.reply_text(answer)

    except Exception as e:
        print("ОШИБКА ТЕКСТА:", e)
        await update.message.reply_text("Ошибка генерации ответа 😔")

# === ЗАПУСК ===
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("БОТ ГОТОВ К РАБОТЕ")

app.run_polling()



