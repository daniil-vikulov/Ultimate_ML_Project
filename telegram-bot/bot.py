import telebot
from telebot import types
from PIL import Image
import os.path
from token_bot import bot, mytoken
import requests
from nudenet import NudeDetector
nude_detector = NudeDetector()


@bot.message_handler(commands=['start'])
def start_function(user_message):
    bot.send_message(user_message.chat.id,
                     f'Привет, {user_message.from_user.first_name}! '
                     f'Проверь свое фото на наличие неприличного контента')


image_cnt = 1


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


bot.polling(none_stop=True)

