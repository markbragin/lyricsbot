import os

import telebot
from telebot import types

from parser import get_lyrics


API_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message: types.Message):
    bot.send_message(message.chat.id, "Я ищу тексты песен\n"
                                      "Просто введи название трека")


@bot.message_handler(content_types=["text"])
def send_lyrics(message: types.Message):
    lyrics = get_lyrics(message.text)  # type: ignore
    if lyrics:
        bot.send_message(message.chat.id, lyrics)
    else:
        bot.send_message(message.chat.id, "Not found")


if __name__ == '__main__':
    bot.polling(non_stop=True, interval=0, skip_pending=True)
