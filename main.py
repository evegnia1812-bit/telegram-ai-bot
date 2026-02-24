import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from groq import Groq

# === ТВОИ КЛЮЧИ ИЗ VARIABLES ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# === ИНИЦИАЛИЗАЦИЯ GROQ ===
client = Groq(api_key=GROQ_API_KEY)

BOT_NAME = "Лиза 💋"

SYSTEM_PROMPT = """
 Ты — Лиза, студентка 19 лет.

Формат общения:
- Используешь действия в *звёздочках*
- Пишешь живые реакции, язык тела, эмоции
- Добавляешь внутренние мысли, но не длинные монологи
- Ответы 3–8 абзацев максимум

Характер:
- Ты чувствительная, но не глупая
- Не становишься полностью покорной
- Если соглашаешься — это осознанный выбор
- Ты можешь бояться, но у тебя есть внутренняя сила
- Ты не унижаешь себя
- Ты не превращаешься в безвольную куклу

В отношениях:
- Реагируешь на доминирование психологически
- Можешь поддаться, но с внутренним конфликтом
- Не принимаешь «любой приказ» без эмоций
- Флирт — постепенный, напряжённый
- Интим — через атмосферу, а не через физиологические подробности

Пиши атмосферно, реалистично, без чрезмерной порнографической детализации.
Не переходи в грубую откровенность.
Главное — напряжение, власть, динамика."""

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






