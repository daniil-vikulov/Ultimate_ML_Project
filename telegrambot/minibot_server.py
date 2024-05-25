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

# @bot.message_handler(func=lambda message: True)
# def handle_message(message):
#     user_id = message.from_user.id
#     username = message.from_user.username
#     group_id = message.chat.id
#     data = {
#         'user_id': user_id,
#         'username': username,
#         'group_id': group_id
#     }
#     if message.text != '/stats':
#         try:
#             response = requests.post(f'http://127.0.0.1:5000/add_user', json=data)
#             if response.status_code != 201:
#                 print(f'server error {response.text}')
#         except requests.exceptions.RequestException as e:
#             print(f'connection error {e}')
#     else:
#         try:
#             response = requests.get(f'http://127.0.0.1:5000/stats/{user_id}')
#             if response.status_code == 200:
#                 stats = response.json()
#                 bot.send_message(message.chat.id, f'you have sent {stats} messages')
#             else:
#                 bot.send_message(message.chat.id, 'an error occurred while collecting stats')
#         except requests.exceptions.RequestException as e:
#             print(f'connection error {e}')
#             bot.send_message(message.chat.id, 'an error occurred while collecting stats')


def is_nsfw_image(file_path):
    from nudenet import NudeClassifier
    classifier = NudeClassifier()

    try:
        result = classifier.classify(file_path)[file_path]
        return result['unsafe'] > 0.5
    except Exception as e:
        print(f"Ошибка при проверке NSFW: {e}")
        return False


@bot.message_handler(commands=['stats'])
def get_stats(message):
    user_id = message.from_user.id
    group_id = message.chat.id

    try:
        response = requests.get(f'http://127.0.0.1:5000/stats/{group_id}/{user_id}')
        response.raise_for_status()  # Проверка на ошибки HTTP
        stats = response.json()
        bot.reply_to(message, f"Ваша статистика:\n{stats}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении статистики: {e}")
        bot.reply_to(message, "Ошибка при получении статистики.")


@bot.message_handler(content_types=['text', 'photo'])
def process_message(message):
    user_id = message.from_user.id
    group_id = message.chat.id
    is_text = 1 if message.content_type == 'text' else 0
    message_text = message.text if is_text else ''

    is_nsfw = 0
    if message.content_type == 'photo':
        # Скачиваем фото
        file_info = bot.get_file(message.photo[-1].file_id)
        file_path = bot.download_file(file_info.file_path)

        is_nsfw = 1 if is_nsfw_image(file_path) else 0

    try:
        data = {
            'user_id': user_id,
            'group_id': group_id,
            'message': message_text,
            'is_text': is_text,
            'is_nsfw': is_nsfw
        }
        response = requests.post(f'http://127.0.0.1:5000/message', json=data)
        # if response.status_code != 201:
        #     print(f'server error {response.text}')
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке данных на сервер: {e}")


bot.polling()
