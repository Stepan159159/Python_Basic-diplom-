import os
import dotenv
import telebot


dotenv.load_dotenv(".env")
x_rapidapi_host = os.getenv("x-rapidapi-host")
x_rapidapi_key = os.getenv("x-rapidapi-key")
bot_token = os.getenv("bot_token")


bot = telebot.TeleBot(bot_token)
