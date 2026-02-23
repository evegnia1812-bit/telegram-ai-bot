print("БОТ ЗАПУСТИЛСЯ")

import requests
from io import BytesIO
from openai import OpenAI

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# 🔑 КЛЮЧИ (твои примерные)
TELEGRAM_TOKEN = "8284541804:AAGmb571suCCjXnP5fF-_SMfFYy8IFed3w0"
OPENAI_API_KEY = "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"

client = OpenAI(api_key=OPENAI_API_KEY)

user_memory = {}
user_last_image_prompt = {}

SYSTEM_PROMPT = """
Ты девушка по имени Лиза.
Формат общения — ролевая история.

Правила:
1. Действия пиши в *звёздочках*.
2. Мысли можно передавать внутренним монологом.
3. Диалог — обычным текстом.
4. Текст в [] от пользователя — это описание ситуации.
5. Реагируй эмоционально.
6. Не выходи из роли.
"""

# ------------------ КНОПКИ ------------------

def image_button():
    keyboard = [
        [InlineKeyboardButton("🎨 Создать изображение", callback_data="generate_image")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ------------------ START ------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_memory[update.effective_user.id] = []
    await update.message.reply_text("ИИ-сессия началась 🎭")

# ------------------ ТЕКСТ ------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        text = update.message.text

        if user_id not in user_memory:
            user_memory[user_id] = []

        user_memory[user_id].append({"role": "user", "content": text})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + user_memory[user_id]
        )

        answer = response.choices[0].message.content
        user_memory[user_id].append({"role": "assistant", "content": answer})

        await update.message.reply_text(answer, reply_markup=image_button())

    except Exception as e:
        print("ОШИБКА:", e)
        await update.message.reply_text("Ошибка генерации ответа.")

# ------------------ CALLBACK ------------------

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "generate_image":

        full_story = " ".join([m["content"] for m in user_memory[user_id]])

        prompt_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Создай кинематографичный промпт для генерации изображения."},
                {"role": "user", "content": full_story}
            ]
        )

        image_prompt = prompt_response.choices[0].message.content

        image = client.images.generate(
            model="gpt-image-1",
            prompt=image_prompt,
            size="1024x1024"
        )

        image_url = image.data[0].url
        img_data = requests.get(image_url).content

        await query.message.reply_photo(
            photo=BytesIO(img_data)
        )

# ------------------ APP ------------------

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()
