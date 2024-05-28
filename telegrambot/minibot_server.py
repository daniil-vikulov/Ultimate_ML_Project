import requests
import telebot
from token_bot import bot, mytoken

image_cnt = 0


@bot.message_handler(commands=['stats'])
def get_stats(message):
    user_id = message.from_user.id
    group_id = message.chat.id

    try:
        response = requests.get(f'http://127.0.0.1:5000/stats/{group_id}/{user_id}')
        response.raise_for_status()
        stats = response.json()
        stats_text = (
            f"Ваша статистика:\n"
            f"Текстовых сообщений: {stats.get('text_messages', 'N/A')}\n"
            f"Безопасных фото: {stats.get('safe_photos', 'N/A')}\n"
            f"NSFW фото: {stats.get('nsfw_photos', 'N/A')}"
        )
        bot.reply_to(message, stats_text)
        graph_url = stats.get('graph_url')
        if graph_url:
            with open(graph_url, 'rb') as g:
                bot.send_photo(message.chat.id, g)
        else:
            bot.reply_to(message, "График активности пользователей недоступен.")
        nsfw_stats_url = stats.get('nsfw_url')
        if nsfw_stats_url:
            with open(nsfw_stats_url, 'rb') as n:
                bot.send_photo(message.chat.id, n)
        else:
            bot.reply_to(message, "График nsfw статистики недоступен")
        top_users_url = stats.get('top_users_url')
        if top_users_url:
            with open(top_users_url, 'rb') as t:
                bot.send_photo(message.chat.id, t)
        else:
            bot.reply_to(message, "График top пользователей недоступен")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении статистики: {e}")
        bot.reply_to(message, "Ошибка при получении статистики.")


@bot.message_handler(func=lambda message: True)
def process_message(message):
    user_id = message.from_user.id
    group_id = message.chat.id
    username = message.from_user.username
    is_text = 1 if message.content_type == 'text' else 0
    message_text = message.text if is_text else ''
    is_nsfw = 0

    try:
        data = {
            'user_id': user_id,
            'group_id': group_id,
            'message': message_text,
            'username': username,
            'is_text': is_text,
            'is_nsfw': is_nsfw
        }
        response = requests.post(f'http://127.0.0.1:5000/message', json=data)
        if response.status_code != 201:
            print(f'server error {response.text}')
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке данных на сервер: {e}")


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
    elif message.content_type == 'document':
        file_id = message.document.file_id
    is_text = 0
    file_info = bot.get_file(file_id)
    file_name = f'image_{image_cnt}.jpg'
    downloaded_file = bot.download_file(file_info.file_path)
    with open(file_name, 'wb') as img:
        img.write(downloaded_file)
    url_detect = f'http://127.0.0.1:5000/detect'
    files = {'file': (file_name, open(file_name, 'rb'), 'image/jpeg')}
    response = requests.post(url_detect, files=files)
    files['file'][1].close()
    if response.status_code == 200:
        result = response.json()
        detected_parts = result['detected_parts']
    face_classes = ['FACE_FEMALE', 'FACE_MALE']
    only_face_classes = all(detection["class"] in face_classes for detection in detected_parts)
    is_nsfw = 0 if only_face_classes else 1
    try:
        data = {
            'user_id': message.from_user.id,
            'group_id': message.chat.id,
            'message': message.text,
            'username': message.from_user.username,
            'is_text': is_text,
            'is_nsfw': is_nsfw
        }
        response = requests.post(f'http://127.0.0.1:5000/message', json=data)
        if response.status_code != 201:
            print(f'server error {response.text}')
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке данных на сервер: {e}")


bot.polling()
