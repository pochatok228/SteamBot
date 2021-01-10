from settings import telegramToken
import telebot

bot = telebot.TeleBot(telegramToken)
bot.send_message(-1001402468429, "Test message")
