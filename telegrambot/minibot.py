import telebot
from token_bot import bot, mytoken
from nudenet import NudeDetector

image_cnt = 0
detector = NudeDetector()


@bot.message_handler(content_types=['photo'])
def photo(message):
    global image_cnt
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_name = f'image_{image_cnt}.jpg'
        downloaded_file = bot.download_file(file_info.file_path)
        with open(file_name, 'wb') as img:
            img.write(downloaded_file)
        bot.send_message(message.chat.id, f"photo image_{image_cnt}.jpg saved successfully")
        detected = detector.detect(f'image_{image_cnt}.jpg')
        if not detected:
            bot.send_message(message.chat.id, "safe")
        else:
            censored = detector.censor(f'image_{image_cnt}.jpg')
            with open(censored, 'rb') as c:
                bot.send_photo(message.chat.id, c)
        image_cnt += 1


bot.polling(none_stop=True)
