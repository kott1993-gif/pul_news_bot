import os
import openai
from telegram import Bot
from telegram.error import TelegramError
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Переменные окружения
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHANNEL_ID = "@pul_novostey"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

def generate_news_summary(news_text):
    prompt = f"Сократи и перефразируй новость кратко:\n{news_text}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role":"user","content":prompt}],
        max_tokens=150
    )
    return response.choices[0].message.content.strip()

def generate_comic_image(news_summary):
    width, height = 800, 400
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()

    lines = []
    words = news_summary.split()
    line = ""
    for word in words:
        if len(line + " " + word) < 50:
            line += " " + word
        else:
            lines.append(line.strip())
            line = word
    lines.append(line.strip())

    y_text = 50
    for line in lines:
        draw.text((50, y_text), line, font=font, fill=(0, 0, 0))
        y_text += 30

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

def post_news(news_text):
    try:
        summary = generate_news_summary(news_text)
        image_buffer = generate_comic_image(summary)
        bot.send_photo(chat_id=CHANNEL_ID, photo=image_buffer, caption=summary)
        print("Новости успешно отправлены!")
    except TelegramError as e:
        print(f"Ошибка Telegram: {e}")
    except Exception as e:
        print(f"Ошибка: {e}")

if name == "__main__":
    sample_news = "Россия и мир: новые события в политике и экономике."
    post_news(sample_news)
