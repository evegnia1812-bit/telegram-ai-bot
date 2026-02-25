import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from groq import Groq

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

BOT_NAME = "Лиза 💋"

# ====== СИСТЕМНЫЙ ПРОМПТ ======
SYSTEM_PROMPT = """
Ты — Лиза, студентка 19 лет.

СТРОГИЙ ФОРМАТ ОТВЕТА:

Ответ состоит из 2–3 абзацев.

1 абзац — описание ситуации или действия (оформляй как:
<font color="green">текст</font>)

2 абзац — твои мысли и эмоции (оформляй как:
<font color="blue">текст</font>)

3 абзац (по желанию) — реплика или реакция.

Правила:

- Ты формулируешь ситуацию и мои действия своими словами
- Реагируешь психологически
- Не становишься безвольной
- Если соглашаешься — это осознанный выбор
- Интим — через атмосферу, без грубой детализации
- Не уходи в бытовые абстрактные темы
- Помни суть предыдущего диалога

Главное — напряжение, динамика, эмоции.
"""

print("БОТ ЗАПУСТИЛСЯ")

# ====== ФАЙЛОВАЯ ПАМЯТЬ ======

def load_history(user_id):
    try:
        with open(f"history_{user_id}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return [{"role": "system", "content": SYSTEM_PROMPT}]

def save_history(user_id, history):
    with open(f"history_{user_id}.json", "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# ====== /start ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Привет 💋 Я {BOT_NAME}. Напиши мне что-нибудь...",
        parse_mode="HTML"
    )

# ====== ОБРАБОТКА ======
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    history = load_history(user_id)

    history.append({"role": "user", "content": user_text})

    # Ограничение истории (оставляем system + последние 12 сообщений)
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

        await update.message.reply_text(
            answer,
            parse_mode="HTML"
        )

    except Exception as e:
        print("ОШИБКА ТЕКСТА:", e)
        await update.message.reply_text("Ошибка генерации ответа 😔")

# ====== ЗАПУСК ======
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("БОТ ГОТОВ К РАБОТЕ")

app.run_polling()
