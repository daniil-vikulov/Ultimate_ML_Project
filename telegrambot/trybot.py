import datetime
import os
import time
import sqlite3

import requests
import telebot
from nudenet.nudenet import NudeDetector
from token_bot import bot
import time

# Добавьте задержку перед подключением
time.sleep(10)
detector = NudeDetector()
server_url = 'http://server:5000'

connection = sqlite3.connect("user_statistics.db", check_same_thread=False)
cursor = connection.cursor()
# cursor.execute("drop table if exists nsfw_content_sent")
cursor.execute("""CREATE TABLE if NOT EXISTS nsfw_content_sent(
user_id INTEGER NOT NULL,
user_name TEXT NOT NULL,
first_name TEXT NOT NULL,
last_name TEXT NOT NULL,
date_time TEXT NOT NULL
)""")


@bot.message_handler(commands=['start'])
def handle_start(message):
    """handles /start command sent in a supergroup or in a personal chat with bot"""
    if message.chat.type == 'supergroup':
        bot.send_message(message.chat.id, f'Привет всем! Этот бот будет следить за порядком в чате\n'
                         f'Нельзя слать неприличные фото, за это бан')
    else:
        bot.send_message(message.chat.id,
                         f'Привет, {message.from_user.first_name}! '
                         f'Проверь свое фото на наличие неприличного контента')


@bot.message_handler(commands=['help'])
def handle_help(message):
    """handles /help command sent in a supergroup or in a personal chat with bot"""
    if message.chat.type == 'supergroup':
        bot.send_message(message.chat.id, f'Если надоел какой-то пользователь, то можно замутить его командой /mute\n'
                                          f'Также можно кикнуть /kick '
                                          f'(просто ответьте на сообщение пользователя, который надоел)\n'
                                          f'Если хотите получить статистику нарушителей чата используйте /stats')
    else:
        bot.send_message(message.chat.id, f'{message.from_user.first_name}!\n'
                                          f'Для того, чтобы протестировать работу сервиса, '
                                          f'воспользуйтесь командой /test или просто отправьте фото\n')


@bot.message_handler(commands=['kick'])
def handle_kick(message):
    """handles /kick command sent in a supergroup, this command can be used to kick users out of the group"""
    if message.chat.type == 'supergroup':
        if message.reply_to_message:
            try:
                user_to_kick = message.reply_to_message.from_user.id
                bot.kick_chat_member(message.chat.id, user_to_kick)
                bot.send_message(message.chat.id, f"Пользователь @{message.reply_to_message.from_user.username}"
                                                  f" был кикнут")
            except Exception as e:
                print(f'Ошибка {e}')
        else:
            bot.send_message(message.chat.id, "Пожалуйста, ответьте на сообщение пользователя, которого надо кикнуть")
    else:
        bot.send_message(message.chat.id, 'К сожалению, такая команда доступна только в группах, для '
                                          'проверки фото воспользуйтесь /test')


@bot.message_handler(commands=['mute'])
def handle_mute(message):
    """handles /mute command sent in a supergroup, this command can be used to mute users in the group"""
    if message.chat.type == 'supergroup':
        if message.reply_to_message:
            try:
                user_to_mute = message.reply_to_message.from_user.id
                mute_seconds = 60
                mute_until = time.time() + mute_seconds
                bot.restrict_chat_member(message.chat.id, user_to_mute, until_date=int(mute_until))
                bot.send_message(message.chat.id, f"Пользователь @{message.reply_to_message.from_user.username}"
                                                  f" замучен на {mute_seconds} секунд.")
            except Exception as e:
                print(f'Ошибка {e}')
        else:
            bot.send_message(message.chat.id, "Пожалуйста, ответьте на сообщение пользователя, которого надо замутить")
    else:
        bot.send_message(message.chat.id, 'К сожалению, такая команда доступна только в группах, для '
                                          'проверки фото воспользуйтесь /test')


@bot.message_handler(commands=['test'])
def handle_test(user_message):
    """handles /test command sent in a personal chat with bot,
    this command is used to check photos for nsfw content"""
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(text="да", callback_data="test.yes"))
    keyboard.add(telebot.types.InlineKeyboardButton(text="нет", callback_data="test.no"))
    bot.send_message(user_message.chat.id, "хотите проверить фото на наличие непристойного контента?",
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("test"))
def write_ans(call):
    """handles callback query of a command /test"""
    if call.message:
        if call.data == "test.yes":
            bot.send_message(call.message.chat.id, "отправьте фото на проверку:)))))))")
        if call.data == "test.no":
            bot.send_message(call.message.chat.id, "квак плак, не больно то надо")


@bot.message_handler(commands=['stats'])
def handle_stats(message):
    """handles /stats command sent in a supergroup,
    this command can be used to know how many nsfw photos user has already sent to a group"""
    if message.chat.type == 'supergroup':
        cursor.execute("SELECT COUNT(*) FROM nsfw_content_sent WHERE user_id = ?", (message.from_user.id,))
        count = cursor.fetchone()[0]
        connection.commit()
        nest_mute_min = 1
        if count == 10:
            bot.send_message(message.chat.id, f'За следующее неприличное фото в чате пользователь {message.from_user.first_name}'
                                              f' {message.from_user.last_name} будет кикнут')
        elif count >= 0 and count <= 2:
            next_mute_min = 1
            bot.send_message(message.chat.id,
                             f'Пользователь {message.from_user.first_name} {message.from_user.last_name} '
                             f'отправил {count} неприличных фото, за следующее - бан на {next_mute_min} минуту')
        elif count >= 3 and count <= 6:
            next_mute_min = 5
            bot.send_message(message.chat.id,
                             f'Пользователь {message.from_user.first_name} {message.from_user.last_name} '
                             f'отправил {count} неприличных фото, за следующее - бан на {next_mute_min} минут')
        elif count >= 7 and count <= 9:
            next_mute_min = 60
            bot.send_message(message.chat.id,
                             f'Пользователь {message.from_user.first_name} {message.from_user.last_name} '
                             f'отправил {count} неприличных фото, за следующее - бан на {next_mute_min} минут')
        else:
            print(f'error')
    else:
        bot.send_message(message.chat.id, f'невозможно узнать статистику')


image_cnt = 0


@bot.message_handler(content_types=['photo', 'document'])
def handle_photo(message):
    """handles sending photos to a supergroup, or a personal chat with bot,
    in case of a supergroup, bot deletes sensitive content and sends blurred version, also mutes the user
    in case of a personal chat, bot tells the user^ that nsfw content was detected"""
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
        # bot.send_message(message.chat.id, f"photo image_{image_cnt}.jpg saved successfully")
        url_detect = f'{server_url}/detect'
        files = {'file': (file_name, open(file_name, 'rb'), 'image/jpeg')}
        response = requests.post(url_detect, files=files)
        files['file'][1].close()
        if response.status_code == 200:
            result = response.json()
            detected_parts = result['detected_parts']
            # print(detected_parts)
        # detected = detector.detect(f'image_{image_cnt}.jpg')
        face_classes = ['FACE_FEMALE', 'FACE_MALE']
        only_face_classes = all(detection["class"] in face_classes for detection in detected_parts)
        cursor.execute("SELECT COUNT(*) FROM nsfw_content_sent WHERE user_id = ?", (message.from_user.id,))
        count = cursor.fetchone()[0]
        connection.commit()
        if message.chat.type == 'supergroup':
            if not detected_parts or only_face_classes:
                bot.send_message(message.chat.id,
                                 "ура ура! фото приличное:)")
                os.remove(file_name)
            else:  # nsfw content sent to a supergroup
                try:
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute(
                        "insert into nsfw_content_sent (user_id, user_name, first_name, last_name, date_time) "
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
                url_censor = f'{server_url}/censor'
                files = {'file': (file_name, open(file_name, 'rb'), 'image/jpeg')}
                response = requests.post(url_censor, files=files)
                files['file'][1].close()
                if response.status_code == 200:
                    answer = response.json()
                    censored = answer.get('censored_image_path')
                    if censored:
                # censored = detector.censor(f'image_{image_cnt}.jpg')
                        with open(censored, 'rb') as c:
                            bot.delete_message(message.chat.id, message.id)
                            bot.send_photo(message.chat.id, c)  # отправили заблюренное фото
                            # if юзер уже кидал порнуху то бан на другое время надо сделать проверку записи в бд
                            user_role = bot.get_chat_member(message.chat.id, message.from_user.id).status
                            if user_role == 'administrator' or user_role == 'creator':
                                bot.send_message(message.chat.id, "нельзя замутить/кикнуть администратора/создателя группы"
                                                                  " за отправление "
                                                                  "нецензурного контента:(")
                            else:
                                try:
                                    mute_seconds = 60
                                    if count > 3:
                                        mute_seconds = 300
                                    if count > 7:
                                        mute_seconds = 3600
                                    if count > 10:
                                        bot.kick_chat_member(message.chat.id, message.from_user.id)
                                        return
                                    mute_until = time.time() + mute_seconds
                                    bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=int(mute_until))
                                except Exception as e:
                                    print(f'Ошибка {e}')
                        os.remove(censored)
                        original = censored.split('_')[0] + '_' + censored.split('_')[1] + '.jpg'
                        os.remove(original)
                    # image_cnt += 1
                    else:
                        bot.send_message(message.chat.id, "Заблюренное фото не найдено:(")
                    image_cnt += 1
                else:
                    bot.send_message(message.chat.id, "Ошибка с блюром фотки:(")
        else:
            if not detected_parts or only_face_classes:
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


@bot.callback_query_handler(func=lambda call: call.data.startswith("next"))
def next_img(call):
    """handles next photo"""
    if call.message.chat.type == 'supergroup':
        return
    else:
        try:
            if call.message:
                name = call.data.split(':')[1]
                os.remove(name)
                bot.send_message(call.message.chat.id, "отправьте следующее фото:)")
        except Exception as e:
            print(f'error {e}')


# @bot.callback_query_handler(func=lambda call: call.data.startswith("colour"))
# def colour(call):
#     if call.message:
#         file_name = call.data.split(':')[2]
#         chosen_colour = call.data.split(':')[1]
#
#         if chosen_colour == "black":
#             censored = censor_colour(file_name, "black")
#         if chosen_colour == "white":
#             censored = censor_colour(file_name, "white")
#         if chosen_colour == "blue":
#             censored = censor_colour(file_name, "blue")
#         if chosen_colour == "red":
#             censored = censor_colour(file_name, "red")
#         if chosen_colour == "green":
#             censored = censor_colour(file_name, "green")
#         if chosen_colour == "orange":
#             censored = censor_colour(file_name, "orange")
#         if chosen_colour == "violet":
#             censored = censor_colour(file_name, "violet")
#         with open(censored, 'rb') as c:
#             bot.send_photo(call.message.chat.id, c)
#         os.remove(censored)
#         original = censored.split('_')[0] + '_' + censored.split('_')[1] + '.jpg'
#         os.remove(original)


@bot.callback_query_handler(func=lambda call: call.data.startswith("colour"))
def colour(call):
    """handles user's choice of colour to blur the picture (for personal chats)"""
    if call.message:
        file_name = call.data.split(':')[2]
        chosen_colour = call.data.split(':')[1]
        url_censor_colour = f'{server_url}/censor_colour?colour={chosen_colour}'
        files = {'file': (file_name, open(file_name, 'rb'), 'image/jpeg')}
        response = requests.post(url_censor_colour, files=files)
        files['file'][1].close()
        if response.status_code == 200:
            try:
                result = response.json()
                censored = os.path.join('../backend/src/app', result.get('censored_image_path'))
                if censored:
                    with open(censored, 'rb') as c:
                        bot.send_photo(call.message.chat.id, c)
                else:
                    print('Заблюренный файл не найден')
            except Exception as e:
                print(f'{e}')


bot.polling(none_stop=True)
