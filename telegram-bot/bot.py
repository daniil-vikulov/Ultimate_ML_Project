import telebot
from telebot import types
from PIL import Image
import os.path
from token_bot import bot, mytoken
import requests
from nudenet import NudeDetector
from telebot import util
from censor import censor_colour
import time

nude_detector = NudeDetector()


@bot.message_handler(commands=['start'])
def start_function(user_message):
    bot.send_message(user_message.chat.id,
                     f'Привет, {user_message.from_user.first_name}! '
                     f'Проверь свое фото на наличие неприличного контента')


@bot.message_handler(commands=['help'])
def help_function(user_message):
    bot.send_message(user_message.chat.id, f"{user_message.from_user.first_name}!\n"
                                           f"Просим заметить, что действует ограничение на количество "
                                           f"бесплатных запросов, максимальное количество = 1 запрос в минуту\n"
                                           f"для того, чтобы протестировать работу сервиса, "
                                           f"воспользуйтесь командой /test \n"
                                           f"Если вы удовлетворены всем функционалом сервиса, предлагаем оплатить "
                                           f"безлимитный доступ. Это можно сделать с помощью команды /pay \n",
                     parse_mode='html')


image_cnt = 1
last_message_time = 0
wait = False


@bot.message_handler(commands=['test'])
def review(user_message):
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


@bot.message_handler(content_types=['photo', 'document'])
def save_and_detect(user_message):
    global image_cnt
    global last_message_time
    global wait
    current_time = time.time()
    left_wait = int(current_time - last_message_time)
    if user_message.content_type == 'photo':
        # if wait:
        #     return
        # if left_wait <= 30:
        #     left_wait = 30 - int(current_time - last_message_time)
        #     bot.send_message(user_message.chat.id, f"вы сможете отправить следующее фото на проверку через {left_wait} "
        #                                            f"секунд")
        #     wait = True
        #     time.sleep(30)
        #     wait = False
            # bot.send_message(user_message.chat.id, "можете отправить фото на проверку!")
        # else:
            # bot.send_message(user_message.chat.id, "можете отправить фото на проверку!")
        file_id = user_message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        photo_url = f'https://api.telegram.org/file/bot{mytoken}/{file_info.file_path}'
        photo = requests.get(photo_url)
        # bot.send_photo(user_message.chat.id, photo.content)
        download_image = bot.download_file(file_info.file_path)
        file_name = f'image_{image_cnt}.jpg'
        with open(file_name, 'wb') as img:
            img.write(download_image)
        # bot.send_message(user_message.chat.id, f'Фото успешно сохранено под названием image_{image_cnt}.jpg')
        detected = nude_detector.detect(f'image_{image_cnt}.jpg')
        face_classes = ['FACE_FEMALE', 'FACE_MALE']
        only_face_classes = all(detection["class"] in face_classes for detection in detected)
        # print(detected)
        if not detected or only_face_classes:
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton(text="дальше", callback_data=f"next:{file_name}"))
            bot.send_message(user_message.chat.id,
                             "ура ура! фото приличное:)",
                             reply_markup=keyboard)
        else:
            # censored_name = censor_black(f'image_{image_cnt}.jpg')
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
            bot.send_message(user_message.chat.id,
                             "в вашем фото был обнаружен непристойный контент, выберите цвет для блюра",
                             reply_markup=keyboard)
        image_cnt += 1
        # last_message_time = current_time
    elif user_message.content_type == 'document':
        # if wait:
        #     return
        # if left_wait <= 30:
        #     left_wait = 30 - int(current_time - last_message_time)
        #     bot.send_message(user_message.chat.id, f"вы сможете отправить следующее фото на проверку через {left_wait} "
        #                                            f"секунд")
        #     wait = True
        #     time.sleep(30)
        #     wait = False
            # bot.send_message(user_message.chat.id, "можете отправить фото на проверку!")
        # else:
        file_id = user_message.document.file_id
        file_info = bot.get_file(file_id)
        photo_url = f'https://api.telegram.org/file/bot{mytoken}/{file_info.file_path}'
        photo = requests.get(photo_url)
        # bot.send_photo(user_message.chat.id, photo.content)
        download_image = bot.download_file(file_info.file_path)
        file_name = f'image_{image_cnt}.jpg'
        with open(file_name, 'wb') as img:
            img.write(download_image)
        # bot.send_message(user_message.chat.id, f'Фото успешно сохранено под названием image_{image_cnt}.jpg')
        detected = nude_detector.detect(f'image_{image_cnt}.jpg')
        # print(detected)
        if not detected:
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton(text="дальше", callback_data=f"next:{file_name}"))
            bot.send_message(user_message.chat.id,
                             "ура ура! фото приличное:)",
                             reply_markup=keyboard)
        else:
            # censored_name = censor_black(f'image_{image_cnt}.jpg')
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
            bot.send_message(user_message.chat.id,
                             "в вашем фото был обнаружен непристойный контент, выберите желаемый цвет для блюра",
                             reply_markup=keyboard)
        image_cnt += 1


@bot.callback_query_handler(func=lambda call: call.data.startswith("next"))
def next_img(call):
    if call.message:
        name = call.data.split(':')[1]
        os.remove(name)
        bot.send_message(call.message.chat.id, "отправьте следующее фото:)")


@bot.callback_query_handler(func=lambda call: call.data.startswith("colour"))
def colour(call):
    if call.message:
        file_name = call.data.split(':')[2]
        chosen_colour = call.data.split(':')[1]
        if chosen_colour == "black":
            censored = censor_colour(file_name, "black")
            with open(censored, 'rb') as c:
                bot.send_photo(call.message.chat.id, c)
            os.remove(censored)
            original = censored.split('_')[0] + '_' + censored.split('_')[1] + '.jpg'
            os.remove(original)
        if chosen_colour == "white":
            censored = censor_colour(file_name, "white")
            with open(censored, 'rb') as c:
                bot.send_photo(call.message.chat.id, c)
            os.remove(censored)
            original = censored.split('_')[0] + '_' + censored.split('_')[1] + '.jpg'
            os.remove(original)
        if chosen_colour == "blue":
            censored = censor_colour(file_name, "blue")
            with open(censored, 'rb') as c:
                bot.send_photo(call.message.chat.id, c)
            os.remove(censored)
            original = censored.split('_')[0] + '_' + censored.split('_')[1] + '.jpg'
            os.remove(original)
        if chosen_colour == "red":
            censored = censor_colour(file_name, "red")
            with open(censored, 'rb') as c:
                bot.send_photo(call.message.chat.id, c)
            os.remove(censored)
            original = censored.split('_')[0] + '_' + censored.split('_')[1] + '.jpg'
            os.remove(original)
        if chosen_colour == "green":
            censored = censor_colour(file_name, "green")
            with open(censored, 'rb') as c:
                bot.send_photo(call.message.chat.id, c)
            os.remove(censored)
            original = censored.split('_')[0] + '_' + censored.split('_')[1] + '.jpg'
            os.remove(original)
        if chosen_colour == "orange":
            censored = censor_colour(file_name, "orange")
            with open(censored, 'rb') as c:
                bot.send_photo(call.message.chat.id, c)
            os.remove(censored)
            original = censored.split('_')[0] + '_' + censored.split('_')[1] + '.jpg'
            os.remove(original)
        if chosen_colour == "violet":
            censored = censor_colour(file_name, "violet")
            with open(censored, 'rb') as c:
                bot.send_photo(call.message.chat.id, c)
            os.remove(censored)
            original = censored.split('_')[0] + '_' + censored.split('_')[1] + '.jpg'
            os.remove(original)

# @bot.message_handler(commands=["pay"])
# def payment():
#     todo


bot.polling(none_stop=True)
