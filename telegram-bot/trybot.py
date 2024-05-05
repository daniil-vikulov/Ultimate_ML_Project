import datetime
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
# cursor.execute("drop table if exists nsfw_stats")
cursor.execute("""CREATE TABLE if NOT EXISTS nsfw_stats(
user_id INTEGER NOT NULL,
user_name TEXT NOT NULL,
first_name TEXT NOT NULL,
last_name TEXT NOT NULL,
date_time TEXT NOT NULL
)""")


@bot.message_handler(commands=['start'])
def handle_start(message):
    if message.chat.type == 'supergroup':
        bot.send_message(message.chat.id, f'Привет всем! Этот бот будет следить за порядком в чате\n'
                         f'Нельзя слать неприличные фото, а также непонятную рекламу, за это бан')
        print(message.chat.id)
    else:
        bot.send_message(message.chat.id,
                         f'Привет, {message.from_user.first_name}! '
                         f'Проверь свое фото на наличие неприличного контента')


@bot.message_handler(commands=['help'])
def handle_help(message):
    if message.chat.id == 'supergroup':
        bot.send_message(message.chat.id, f'Если надоел какой-то пользоваель, то можно замутить его командой /mute\n'
                                          f'Также можно кикнуть /kick '
                                          f'(просто ответьте на сообщение пользователя, который надоел)\n'
                                          f'Если хотите получить статистику нарушителей чата используйте /stats')
    else:
        bot.send_message(message.chat.id, f"{message.from_user.first_name}!\n"
                                          f"Для того, чтобы протестировать работу сервиса, "
                                          f"воспользуйтесь командой /test или просто отправьте фото\n")


@bot.message_handler(commands=['kick'])
def handle_kick(message):
    if message.chat.id == 'supergroup':
        if message.reply_to_message:
            try:
                user_to_kick = message.reply_to_message.from_user.id
                bot.kick_chat_member(message.chat.id, user_to_kick)
                bot.send_message(message.chat.id, f"User {user_to_kick} has been kicked.")
            except Exception as e:
                print(f'Ошибка {e}')
        else:
            bot.send_message(message.chat.id, "Please reply to the user you want to kick.")
    else:
        bot.send_message(message.chat.id, 'К сожалению, такая команда доступна только в группах, для '
                                          'проверки фото воспользуйтесь /test')


@bot.message_handler(commands=['mute'])
def handle_mute(message):
    if message.chat.id == 'supergroup':
        if message.reply_to_message:
            try:
                user_to_mute = message.reply_to_message.from_user.id
                mute_seconds = 60
                mute_until = time.time() + mute_seconds
                bot.restrict_chat_member(message.chat.id, user_to_mute, until_date=int(mute_until))
                bot.send_message(message.chat.id, f"User {user_to_mute} has been muted for {mute_seconds} seconds.")
            except Exception as e:
                print(f'Ошибка {e}')
        else:
            bot.send_message(message.chat.id, "Please reply to the user you want to mute.")
    else:
        bot.send_message(message.chat.id, 'К сожалению, такая команда доступна только в группах, для '
                                          'проверки фото воспользуйтесь /test')


@bot.message_handler(commands=['test'])
def handle_test(user_message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(text="да", callback_data="test.yes"))
    keyboard.add(telebot.types.InlineKeyboardButton(text="нет", callback_data="test.no"))
    bot.send_message(user_message.chat.id, "хотите проверить фото на наличие непристойного контента?",
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("test"))
def write_ans(call):
    if call.message:
        if call.data == "test.yes":
            bot.send_message(call.message.chat.id, "отправьте фото на проверку:)))))))")
        if call.data == "test.no":
            bot.send_message(call.message.chat.id, "квак плак, не больно то надо")


# @bot.message_handler(commands=['stats'])
# def handle_stats(message):
# todo


image_cnt = 0


@bot.message_handler(content_types=['photo', 'document'])
def handle_photo(message):
    global image_cnt
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
        if message.chat.type == 'supergroup':
            if not detected or only_face_classes:
                bot.send_message(message.chat.id,
                                 "ура ура! фото приличное:)")
                os.remove(file_name)
            else:
                try:
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute(
                        "insert into nsfw_stats (user_id, user_name, first_name, last_name, date_time) "
                        "values (?, ?, ?, ?, ?)",
                        (message.from_user.id, message.from_user.username,
                         message.from_user.first_name, message.from_user.last_name, current_time))
                    connection.commit()
                except Exception as e:
                    print(f"Ошибка записи в базу данных: {e}")

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
                            print(f'Ошибка {e}')
                os.remove(censored)
                original = censored.split('_')[0] + '_' + censored.split('_')[1] + '.jpg'
                os.remove(original)
            image_cnt += 1
        else:
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
