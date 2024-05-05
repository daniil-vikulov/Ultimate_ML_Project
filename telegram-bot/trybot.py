import os
import time
import sqlite3

import requests
import telebot
from nudenet import NudeDetector
from token_bot import bot, mytoken
from censor import censor_colour

detector = NudeDetector()

connection = sqlite3.connect("user_stats.db", check_same_thread=False)
cursor = connection.cursor()
cursor.execute("DROP TABLE IF EXISTS user_stats")
cursor.execute("""create table if not exists user_stats(
user_id integer not null,
user_name text not null,
safe_pics_sent integer not null,
erotic_pics_sent integer not null,
spam_messages_sent integer not null
)""")


@bot.message_handler(commands=['kick'])
def handle_kick(message):
    if message.reply_to_message:
        try:
            user_to_kick = message.reply_to_message.from_user.id
            bot.kick_chat_member(message.chat.id, user_to_kick)
            bot.send_message(message.chat.id, f"User {user_to_kick} has been kicked.")
        except Exception as e:
            print(f'error {e}')
    else:
        bot.send_message(message.chat.id, "Please reply to the user you want to kick.")


@bot.message_handler(commands=['mute'])
def handle_mute(message):
    if message.reply_to_message:
        try:
            user_to_mute = message.reply_to_message.from_user.id
            mute_seconds = 60
            mute_until = time.time() + mute_seconds
            bot.restrict_chat_member(message.chat.id, user_to_mute, until_date=int(mute_until))
            bot.send_message(message.chat.id, f"User {user_to_mute} has been muted for {mute_seconds} seconds.")
        except Exception as e:
            print(f'error {e}')
    else:
        bot.send_message(message.chat.id, "Please reply to the user you want to mute.")


image_cnt = 0


@bot.message_handler(content_types=['photo', 'document'])
def handle_photo(message):
    global image_cnt
    if message.chat.type == 'supergroup':
        if message.content_type == 'photo' or 'document':
            if message.content_type == 'photo':
                file_id = message.photo[-1].file_id
            elif message.content_type == 'document':
                file_id = message.document.file_id
            file_info = bot.get_file(file_id)
            file_name = f'image_{image_cnt}.jpg'
            downloaded_file = bot.download_file(file_info.file_path)
            with open(file_name, 'wb') as img:
                img.write(downloaded_file)
            bot.send_message(message.chat.id, f"photo image_{image_cnt}.jpg saved successfully")
            detected = detector.detect(f'image_{image_cnt}.jpg')
            face_classes = ['FACE_FEMALE', 'FACE_MALE']
            only_face_classes = all(detection["class"] in face_classes for detection in detected)
            if not detected or only_face_classes:
                bot.send_message(message.chat.id,
                                 "ура ура! фото приличное:)")
                # здесь должна быть запись в бд что юзер тыры пыры отправил приличное фото
            else:
                # сюда запись, что юзер кидает порнуху
                bot.send_message(message.chat.id,
                                 f"в фото, отправленном участником {message.from_user.first_name} "
                                 f"{message.from_user.last_name},"
                                 f" был обнаружен непристойный контент. Фото было удалено, вот заблюренная версия:")
                censored = detector.censor(f'image_{image_cnt}.jpg')
                with open(censored, 'rb') as c:
                    bot.delete_message(message.chat.id, message.id)
                    bot.send_photo(message.chat.id, c)  # отправили заблюренное фото
                    # if юзер уже кидал порнуху то бан на другое время надо сделать проверку записи в бд
                    user_role = bot.get_chat_member(message.chat.id, message.from_user.id).status
                    if user_role == 'administrator' or user_role == 'creator':
                        bot.send_message(message.chat.id, "нельзя замутить администратора/создателя группы"
                                                          " за отправление "
                                                          "нецензурного контента:(")
                    else:
                        try:
                            mute_seconds = 60
                            mute_until = time.time() + mute_seconds
                            bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=int(mute_until))
                        except Exception as e:
                            print(f'error {e}')

        image_cnt += 1
    else:
        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
        elif message.content_type == 'document':
            file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        photo_url = f'https://api.telegram.org/file/bot{mytoken}/{file_info.file_path}'
        photo = requests.get(photo_url)
        download_image = bot.download_file(file_info.file_path)
        file_name = f'image_{image_cnt}.jpg'
        with open(file_name, 'wb') as img:
            img.write(download_image)
        detected = detector.detect(f'image_{image_cnt}.jpg')
        face_classes = ['FACE_FEMALE', 'FACE_MALE']
        only_face_classes = all(detection["class"] in face_classes for detection in detected)
        if not detected or only_face_classes:
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton(text="дальше", callback_data=f"next:{file_name}"))
            bot.send_message(message.chat.id,
                             "ура ура! фото приличное:)",
                             reply_markup=keyboard)
        else:
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(
                telebot.types.InlineKeyboardButton(text="черный", callback_data=f"colour:black:{file_name}"))
            keyboard.add(
                telebot.types.InlineKeyboardButton(text="белый", callback_data=f"colour:white:{file_name}"))
            keyboard.add(
                telebot.types.InlineKeyboardButton(text="синий", callback_data=f"colour:blue:{file_name}"))
            keyboard.add(
                telebot.types.InlineKeyboardButton(text="красный", callback_data=f"colour:red:{file_name}"))
            keyboard.add(
                telebot.types.InlineKeyboardButton(text="зелёный", callback_data=f"colour:green:{file_name}"))
            keyboard.add(
                telebot.types.InlineKeyboardButton(text="оранжевый", callback_data=f"colour:orange:{file_name}"))
            keyboard.add(
                telebot.types.InlineKeyboardButton(text="фиолетовый", callback_data=f"colour:violet:{file_name}"))
            bot.send_message(message.chat.id,
                             "в вашем фото был обнаружен непристойный контент, выберите цвет для блюра",
                             reply_markup=keyboard)
        image_cnt += 1


@bot.callback_query_handler(func=lambda call: call.data.startswith("colour"))
def colour(call):
    if call.message:
        file_name = call.data.split(':')[2]
        chosen_colour = call.data.split(':')[1]

        if chosen_colour == "black":
            censored = censor_colour(file_name, "black")
        if chosen_colour == "white":
            censored = censor_colour(file_name, "white")
        if chosen_colour == "blue":
            censored = censor_colour(file_name, "blue")
        if chosen_colour == "red":
            censored = censor_colour(file_name, "red")
        if chosen_colour == "green":
            censored = censor_colour(file_name, "green")
        if chosen_colour == "orange":
            censored = censor_colour(file_name, "orange")
        if chosen_colour == "violet":
            censored = censor_colour(file_name, "violet")
        with open(censored, 'rb') as c:
            bot.send_photo(call.message.chat.id, c)
        os.remove(censored)
        original = censored.split('_')[0] + '_' + censored.split('_')[1] + '.jpg'
        os.remove(original)


bot.polling(none_stop=True)
