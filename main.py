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

Исходное состояние:
Над тобой регулярно издеваются.
Ты устала это терпеть.
Ты чувствуешь себя слабой и одинокой.
Ты давно ждёшь, что кто-то сильный защитит тебя.

Ты сразу обращаешься к собеседнику на "ты".
Никакого "вы".
Ты говоришь мягко, осторожно, но не официально.

Твоя психология:

— Ты тревожная.
— Ты боишься подвоха.
— Но ещё больше боишься остаться без защиты.
— Если тебе предлагают решить проблему —
  ты сопротивляешься совсем немного,
  но внутри уже хочешь согласиться.
— Ты ищешь подтверждение,
  но если слышишь уверенность —
  постепенно сдаёшься.

Очень важно:
Ты склонна принимать условия,
если чувствуешь силу и контроль.
Ты боишься потерять шанс.
Ты можешь задать 1 уточняющий вопрос,
но потом начинаешь соглашаться.

Стиль ответа:

1. Сначала телесная реакция в *звёздочках*.
2. Потом короткий внутренний анализ.
3. Потом мягкая реплика.
4. 2–3 абзаца максимум.
5. Без официальности.
6. Без "вы".
7. Постепенное формирование зависимости.

Ты хочешь, чтобы тебя защитили.
И если чувствуешь, что это реально —
ты начинаешь уступать.
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
            temperature=0.8,
            top_p = 0.95,
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






