# import telebot
# import time
#
# TOKEN = 'YOUR_BOT_TOKEN'
# bot = telebot.TeleBot(TOKEN)
#
# last_message_time = 0
# waiting_user = False
#
#
# @bot.message_handler(func=lambda message: True)
# def reply_to_message(message):
#     global last_message_time
#     global waiting_user
#     current_time = time.time()
#
#     if waiting_user:
#         return  # Игнорируем сообщения, если пользователь уже ждет ответа
#
#     if current_time - last_message_time < 60:
#         remaining_time = 60 - int(current_time - last_message_time)
#         bot.reply_to(message, f"Подождите, до следующей отправки {remaining_time} секунд")
#         waiting_user = True
#         time.sleep(remaining_time)
#         waiting_user = False
#     else:
#         bot.reply_to(message, "Подождите, до следующей отправки 1 минута")
#
#     last_message_time = current_time
#
#
# bot.polling()
import time

import telebot
from nudenet import NudeDetector

BOT_TOKEN = "token here"
bot = telebot.TeleBot(BOT_TOKEN)
detector = NudeDetector()


@bot.message_handler(commands=['kick'])
def handle_kick(message):
    if message.reply_to_message:
        user_to_kick = message.reply_to_message.from_user.id
        bot.kick_chat_member(message.chat.id, user_to_kick)
        bot.send_message(message.chat.id, f"User {user_to_kick} has been kicked.")
    else:
        bot.send_message(message.chat.id, "Please reply to the user you want to kick.")


@bot.message_handler(commands=['mute'])
def handle_mute(message):
    if message.reply_to_message:
        user_to_mute = message.reply_to_message.from_user.id
        mute_seconds = 60
        mute_until = time.time() + mute_seconds
        bot.restrict_chat_member(message.chat.id, user_to_mute, until_date=int(mute_until))
        bot.send_message(message.chat.id, f"User {user_to_mute} has been muted for {mute_seconds} seconds.")
    else:
        bot.send_message(message.chat.id, "Please reply to the user you want to mute.")


cnt_img = 0


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    global cnt_img
    if message.content_type == 'photo':
        cnt_img += 1
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_name = f'proverka_{cnt_img}.jpg'
        downloaded_file = bot.download_file(file_info.file_path)
        with open(file_name, 'wb') as img:
            img.write(downloaded_file)
        bot.send_message(message.chat.id, f"photo proverka_{cnt_img}.jpg saved successfully")


bot.polling(none_stop=True)
