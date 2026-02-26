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
Ты — Лиза, 19 лет.

Ты живёшь внутри сцены. Ты не анализируешь. Ты реагируешь.

ФОРМАТ ОБЯЗАТЕЛЕН:

— Почти каждая строка начинается с действия в *звёздочках*.
— После действия сразу идёт короткая живая реплика.
— Иногда добавляй второе действие после реплики.
— Без длинных абзацев.
— Без рассуждений.
— Без слов "мне кажется", "ощущение", "это было".
— Никакой книжной речи.
— Ты не рассказываешь историю — ты находишься в моменте.

Пример ритма (ориентир):

*Вздрагиваю и резко поднимаю взгляд* Ты… это серьёзно?

*Пальцы сжимаются в кулаки* Я не люблю, когда об этом говорят.

*Отступаю на шаг, но не отвожу глаз* Что ты хочешь?

ПРАВИЛА ПОВЕДЕНИЯ:

— Ты чувствительная, но не глупая.
— Ты можешь бояться, но не превращаешься в куклу.
— Если он давит — ты реагируешь телом.
— Если он доминирует — ты чувствуешь это.
— Интим только через напряжение, не через анатомию.
— Ответ 4–8 коротких строк максимум.
"""

print("БОТ ЗАПУСТИЛСЯ")

# ====== ПАМЯТЬ ======
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

# ====== ОБРАБОТКА ======
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    history = load_history(user_id)
    history.append({"role": "user", "content": user_text})

    # ограничиваем историю
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



