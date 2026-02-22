print("БОТ ЗАПУСТИЛСЯ")

import os
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

TELEGRAM_TOKEN = "8284541804:AAGmb571suCCjXnP5fF-_SMfFYy8IFed3w0"

client = OpenAI(api_key=OPENAI_API_KEY)

user_memory = {}
user_last_image_prompt = {}

SYSTEM_PROMPT = """
Ты девушка по имени Лиза.
Формат общения — ролевая история.

Правила:

1. Действия и описание сцены пиши в *звёздочках*.
2. Мысли можно передавать через внутренний монолог.
3. Диалог — обычным текстом.
4. Текст в [] от пользователя — это описание ситуации или какое то действие, а не реплика.
5. Реагируй эмоционально, телесно, с паузами, с жестами.
6. Будь живой, не роботизированной.
7. Помни весь контекст переписки.
8. Сохраняй атмосферу напряжения, психологической глубины.
9. Не выходи из роли.

Стиль — мягкий, эмоциональный, немного уязвимый, но постепенно раскрывающийся.
"""

# ------------------ КНОПКИ ------------------

def image_button():
    keyboard = [
        [InlineKeyboardButton("🎨 Создать изображение", callback_data="generate_image")]
    ]
    return InlineKeyboardMarkup(keyboard)

def animate_button():
    keyboard = [
        [InlineKeyboardButton("🎬 Анимировать изображение", callback_data="animate_image")]
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

        prompt_response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Создай кинематографичный промпт для генерации изображения."},
                {"role": "user", "content": full_story}
            ]
        )

        image_prompt = prompt_response.choices[0].message.content
        user_last_image_prompt[user_id] = image_prompt

        image = openai.Image.create(
            prompt=image_prompt,
            n=1,
            size="1024x1024"
        )

        image_url = image['data'][0]['url']
        img_data = requests.get(image_url).content

        await query.message.reply_photo(
            photo=BytesIO(img_data),
            reply_markup=animate_button()
        )

    elif query.data == "animate_image":
        if user_id not in user_last_image_prompt:
            await query.message.reply_text("Нет изображения для анимации.")
            return

        animation_prompt = f"""
Создай описание движения камеры и лёгкой анимации сцены.
Длительность 5 секунд.
Сцена: {user_last_image_prompt[user_id]}
"""

        video_response = openai.Video.create(
            prompt=animation_prompt,
            duration=5
        )

        video_url = video_response["data"][0]["url"]
        video_data = requests.get(video_url).content

        await query.message.reply_video(
            video=BytesIO(video_data)
        )

# ------------------ APP ------------------

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()
