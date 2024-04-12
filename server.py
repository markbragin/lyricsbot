import os

import telebot
from telebot import types

from client import get_formatted_answer


API_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")

if not API_TOKEN:
    print("Set telegram bot api token as environment variable")
    exit()

BUFFER_SIZE = 4096

bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message: types.Message):
    bot.send_message(
        message.chat.id, "Я ищу тексты песен\n" "Просто введи название трека"
    )


@bot.message_handler(content_types=["text"])
def send_lyrics(message: types.Message):
    text = get_formatted_answer(str(message.text))
    if text:
        for msg in _split_into_valid_messages(text):
            bot.send_message(
                message.chat.id,
                msg,
                disable_web_page_preview=True,
            )
    else:
        bot.send_message(message.chat.id, "Not found")


def _split_into_valid_messages(text: str) -> list[str]:
    messages = []
    l_idx = 0
    while len(text[l_idx:]) > BUFFER_SIZE:
        offset = text[l_idx:].rfind("[", 0, BUFFER_SIZE)
        if offset == -1 or offset == 0:
            offset = text[l_idx:].rfind("\n", 0, BUFFER_SIZE)
        r_idx = l_idx + offset
        messages.append(text[l_idx:r_idx])
        l_idx = r_idx
    messages.append(text[l_idx:])
    return messages


if __name__ == "__main__":
    bot.polling(non_stop=True, interval=0, skip_pending=True, timeout=0)
