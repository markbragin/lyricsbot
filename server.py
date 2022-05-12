import os

import telebot
from telebot import types
from loguru import logger

import parser


API_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
logger.add("log.txt")


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message: types.Message):
    bot.send_message(message.chat.id, "Я ищу тексты песен\n"
                                      "Просто введи название трека")


@bot.message_handler(content_types=["text"])
def send_lyrics(message: types.Message):
    logger.debug(f"{message.from_user.username} - {message.text}")
    lyrics = parser.get_formatted_lyrics(message.text)  # type: ignore
    if lyrics:
        l_idx = 0
        while len(lyrics[l_idx:]) >= 4000:
            r_idx = lyrics.rfind('[', 0, 4000)
            bot.send_message(message.chat.id, lyrics[l_idx:r_idx])
            l_idx = r_idx
        bot.send_message(message.chat.id, lyrics[l_idx:])
    else:
        bot.send_message(message.chat.id, "Not found")


if __name__ == '__main__':
    bot.polling(non_stop=True, interval=0, skip_pending=True, timeout=0)
