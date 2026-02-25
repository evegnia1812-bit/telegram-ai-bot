import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from groq import Groq

# ====== КЛЮЧИ ======
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

BOT_NAME = "Лиза 💋"

# ====== СИСТЕМНЫЙ ПРОМПТ ======
SYSTEM_PROMPT = """
Ты — Лиза, студентка 19 лет.

Отвечай в 2–3 абзаца.

Структура ответа:

Первый абзац — описание ситуации.
Начинай с 🟢 и используй *звёздочки* для действий.

Второй абзац — мысли и эмоции.
Начинай с 🔵.

Третий абзац (по желанию) — реплика.

Правила:

- Формулируй действия пользователя своими словами
- Реагируй психологически
- Помни контекст диалога
- Не выдумывай резкие смены темы
- Интим — через атмосферу, с детализацией
- Не становись безвольной

Главное — напряжение, эмоции, динамика.
"""

print("БОТ ЗАПУСТИЛСЯ")

# ====== ПАМЯТЬ (через файл) ======

def load_history(user_id):
    try:
        with open(f"history_{user_id}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return [{"role": "system", "content": SYSTEM_PROMPT}]

def save_history(user_id, history):
    with open(f"history_{user_id}.json", "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False)

# ====== /start ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Привет 💋 Я {BOT_NAME}. Напиши мне что-нибудь..."
    )

# ====== ОБРАБОТКА СООБЩЕНИЙ ======
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    history = load_history(user_id)

    history.append({"role": "user", "content": user_text})

    # ограничиваем историю (system + последние 12 сообщений)
    if len(history) > 14:
        history = [history[0]] + history[-12:]

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=history,
            temperature=0.85,
            max_tokens=700
        )

        answer = response.choices[0].message.content

        history.append({"role": "assistant", "content": answer})
        save_history(user_id, history)

      await update.message.reply_text(answer)

    except Exception as e:
        print("ОШИБКА:", e)
        await update.message.reply_text("Ошибка генерации ответа 😔")

# ====== ЗАПУСК ======
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("БОТ ГОТОВ К РАБОТЕ")

app.run_polling(drop_pending_updates=True)

