import telebot
from telebot import types
from PIL import Image
import os.path
from token_bot import bot, mytoken
import requests
from nudenet import NudeDetector
from telebot import util

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


@bot.message_handler(commands=['test'])
def review(user_message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(text="да", callback_data="test.yes"))
    bot.send_message(user_message.chat.id, "хотите проверить фото на наличие непристойного контента?",
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("test"))
def write_ans(call):
    if call.message:
        bot.send_message(call.message.chat.id, "отправьте фото на проверку:)))))))")


@bot.message_handler(content_types=['photo', 'document'])
def save_and_send_back(user_message):
    global image_cnt
    if user_message.content_type == 'photo':
        file_id = user_message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        photo_url = f'https://api.telegram.org/file/bot{mytoken}/{file_info.file_path}'
        photo = requests.get(photo_url)
        # bot.send_photo(user_message.chat.id, photo.content)
        download_image = bot.download_file(file_info.file_path)
        file_name = f'image_{image_cnt}.jpg'
        with open(file_name, 'wb') as img:
            img.write(download_image)
        bot.send_message(user_message.chat.id, f'Фото успешно сохранено под названием image_{image_cnt}.jpg')
        # detected = nude_detector.detect(f'image_{image_cnt}.jpg')
        # if detected is None:
        #     bot.send_photo(user_message.chat.id, photo.content)
        # else:
            # keyboard = telebot.types.InlineKeyboardMarkup()
            # keyboard.add(telebot.types.InlineKeyboardButton(text="черный", callback_data="colour.black"))
            # bot.send_message(user_message.chat.id,
            #                  "в вашем фото был обнаружен непристойный контент, выберите цвет для блюра",
            #                  reply_markup=keyboard)
            # bot.register_next_step_handler(user_message, lambda m: colour(m, file_name))
        censored = open(nude_detector.censor(f'image_{image_cnt}.jpg'), 'rb')
        bot.send_photo(user_message.chat.id, censored)
        censored.close()
        image_cnt += 1
    elif user_message.content_type == 'document':
        file_id = user_message.document.file_id
        file_info = bot.get_file(file_id)
        photo_url = f'https://api.telegram.org/file/bot{mytoken}/{file_info.file_path}'
        photo = requests.get(photo_url)
        # bot.send_photo(user_message.chat.id, photo.content)
        download_image = bot.download_file(file_info.file_path)
        file_name = f'image_{image_cnt}.jpg'
        with open(file_name, 'wb') as img:
            img.write(download_image)
        bot.send_message(user_message.chat.id, f'Фото успешно сохранено под названием image_{image_cnt}.jpg')
        censored = open(nude_detector.censor(f'image_{image_cnt}.jpg'), 'rb')
        bot.send_photo(user_message.chat.id, censored)
        censored.close()
        image_cnt += 1


# def colour(user_message, file_name):
#     chosen_colour = user_message.text.lower()
#     if chosen_colour == "черный":
#         censored = open(nude_detector.censor(f'image_{image_cnt}.jpg'), 'rb')
#         bot.send_photo(user_message.chat.id, censored)
#         censored.close()


# @bot.callback_query_handler(func=lambda call: call.data.startswith("colour"))
# def colour(call):
#     if call.message:
#         if call.data == "colour.black":
#             censored = open(nude_detector.censor(f'image_{image_cnt}.jpg'), 'rb')
#             bot.send_photo(call.message.chat.id, censored)
#             censored.close()
#             bot.send_photo(call.message.chat.id, censored)

# @bot.message_handler(commands=["pay"])
# def payment():
#


bot.polling(none_stop=True)
