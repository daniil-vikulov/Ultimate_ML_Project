import telebot
from telebot import types
from PIL import Image
import os

bot = telebot.TeleBot('token here')


@bot.message_handler(commands=['start'])
def start_function(user_message):
    bot.send_message(user_message.chat.id,
                     f'Привет, {user_message.from_user.first_name}! '
                     f'Проверь свое фото на наличие неприличного контента')


image_cnt = 1


@bot.message_handler(content_types=['photo', 'document'])
def handle_sent_images(user_message):
    global image_cnt
    if user_message.content_type == 'photo':
        file_id = user_message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        download_image = bot.download_file(file_info.file_path)
        file_name = f'image_{image_cnt}.jpg'
        with open(file_name, 'wb') as img:
            img.write(download_image)
        bot.send_message(user_message.chat.id, f'Фото успешно сохранено под названием image_{image_cnt}.jpg')
        image_cnt += 1
    elif user_message.content_type == 'document':
        file_id = user_message.document.file_id
        file_info = bot.get_file(file_id)
        download_image = bot.download_file(file_info.file_path)
        file_name = f'image_{image_cnt}.png'
        with open(file_name, 'wb') as img:
            img.write(download_image)
        bot.send_message(user_message.chat.id, f'Фото успешно сохранено под названием image_{image_cnt}.jpg')
        image_cnt += 1
    else:
        bot.send_message('Пожалуйста отправьте файл, либо фото (в форматах .jpg или .png)')


bot.polling(none_stop=True)

