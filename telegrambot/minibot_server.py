import requests
import telebot
from token_bot import bot, mytoken

image_cnt = 0


# @bot.message_handler(content_types=['photo'])
# def photo(message):
#     global image_cnt
#     if message.content_type == 'photo':
#         file_id = message.photo[-1].file_id
#         file_info = bot.get_file(file_id)
#         downloaded_file = bot.download_file(file_info.file_path)
#
#         file_name = f'image_{image_cnt}.jpg'
#         with open(file_name, 'wb') as img:
#             img.write(downloaded_file)
#
#         url = 'http://127.0.0.1:5000/censor'
#         files = {'file': (file_name, open(file_name, 'rb'), 'image/jpeg')}
#         response = requests.post(url, files=files)
#         files['file'][1].close()  # Закрытие файла после отправки
#
#         if response.status_code == 200:
#             result = response.json()
#             censored_image_path = result.get('censored_image_path')
#             if censored_image_path:
#                 with open(censored_image_path, 'rb') as photo_file:
#                     bot.send_photo(message.chat.id, photo_file)
#             else:
#                 bot.send_message(message.chat.id, "Censored image not found")
#         else:
#             bot.send_message(message.chat.id, "Error processing image")
#
#         image_cnt += 1

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    username = message.from_user.username
    group_id = message.chat.id
    data = {
        'user_id': user_id,
        'username': username,
        'group_id': group_id
    }
    if message.text != '/stats':
        try:
            response = requests.post(f'http://127.0.0.1:5000/add_user', json=data)
            if response.status_code != 201:
                print(f'server error {response.text}')
        except requests.exceptions.RequestException as e:
            print(f'connection error {e}')
    else:
        try:
            response = requests.get(f'http://127.0.0.1:5000/stats/{user_id}')
            if response.status_code == 200:
                stats = response.json()
                bot.send_message(message.chat.id, f'you have sent {stats} messages')
            else:
                bot.send_message(message.chat.id, 'an error occurred while collecting stats')
        except requests.exceptions.RequestException as e:
            print(f'connection error {e}')
            bot.send_message(message.chat.id, 'an error occurred while collecting stats')


bot.polling()
