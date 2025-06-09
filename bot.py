from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data['status'] == 'ok':
            articles = data['articles'][:5]
            news_text = "\n\n".join([f"{a['title']}\n{a['url']}" for a in articles])
            await update.message.reply_text(news_text)
        else:
            await update.message.reply_text("Sorry, I couldn't fetch the news right now.")
            logger.warning("Problem fetching news: %s", data)

    except requests.exceptions.RequestException as e:
        await update.message.reply_text("I’m having trouble connecting to the news service.")
        logger.error("Connection error in news(): %s", e)
    except Exception as e:
        await update.message.reply_text("Something went wrong.")
        logger.error("Unexpected error in news(): %s", e)


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Hey! Please tell me a city, like: /weather London")
        return
    
    city = " ".join(context.args)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=en"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('cod') != 200:
            await update.message.reply_text(f"Oops, I couldn’t find '{city}'. Check the spelling?")
            logger.warning("City not found: %s", city)
        else:
            description = data['weather'][0]['description']
            temperature = data['main']['temp']
            await update.message.reply_text(f"Here’s the weather in {city}:\n{description.capitalize()}\nTemp: {temperature}°C")

    except requests.exceptions.RequestException as e:
        await update.message.reply_text("Sorry, I’m having trouble connecting to the weather service.")
        logger.error("Connection error in weather(): %s", e)
    except Exception as e:
        await update.message.reply_text("Oops, something unexpected happened.")
        logger.error("Unexpected error in weather(): %s", e)


if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("weather", weather))

    print("Bot is up and running!")
    app.run_polling()
