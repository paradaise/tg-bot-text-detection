from PIL import Image, ImageEnhance, ImageFilter, ImageOps

import numpy as np
from ultralytics import YOLO  # Assuming YOLOv8 is used
import easyocr
import  matplotlib.pyplot as plt
import io
import telebot
from telebot import types


def preprocess_image(image):
    # Изменение размера изображения
    image = image.resize((image.width * 2, image.height * 2), Image.LANCZOS)

    # Усиление контраста изображения
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.5)

    # Преобразование в оттенки серого и применение адаптивной бинаризации
    image = image.convert('L')
    image = ImageOps.invert(image)  # Инвертируем цвета для лучшего распознавания
    image = image.filter(ImageFilter.MedianFilter(size=1))  # Применяем медианный фильтр для удаления шума

    return image

def perform_ocr(image):
    # Инициализация OCR
    reader = easyocr.Reader(['ru', 'en'],gpu= True)

    # Выполнение OCR
    result = reader.readtext(np.array(image))

    # Сбор данных из результатов OCR
    boxes = []
    txts = []
    scores = []

    for line in result:
        boxes.append(line[0])
        txts.append(line[1])
        scores.append(line[2])

    return boxes, txts, scores

def crop_and_ocr(img_path):
    results = yolo(img_path)
    regions = [box.xyxy[0].cpu().numpy().tolist() for reg in results for box in reg.boxes] if results[0].boxes is not None else []

    image = Image.open(img_path).convert('RGB')

    if regions:

        result_msg = 'Вот что мне удалось увидеть:\n'

        for i, region in enumerate(regions):

            cropped_image = image.crop(region)
            cropped_image = preprocess_image(cropped_image)
            boxes, txts, scores = perform_ocr(cropped_image)
            result_img = io.BytesIO()
            cropped_image.save(result_img, format='PNG')
            result_img = result_img.getvalue()

            for txt, score in zip(txts, scores):
                if (score > 0.2 and regions):
                    result_msg += f"{txt}: {score:.2f}%\n"

        return result_msg,result_img
    else:
        result_msg = 'Мне ничего не удалось найти.Попробуйте другое фото'
        return result_msg, None

    
yolo = YOLO('best.pt')

#################################################################BOT##############################################

TOKEN = '7042756970:AAG2mR7hGBlygSvMHlEp9gdfxjHlrvzQd_k'
bot = telebot.TeleBot(TOKEN)

main_menu = ('📑Контакты','🔗Другое','💸Поддержать')
donation_menu = ('🫰Юмани','💰СБП','↩️Назад')

def keyboard(menu):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    info = types.KeyboardButton(menu[0])
    other = types.KeyboardButton(menu[1])
    donation = types.KeyboardButton(menu[2])
    markup.add(info,other,donation)
    return markup


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "📸Привет,отправь мне фотографию и посмотри что получится!",reply_markup = keyboard(main_menu))

@bot.message_handler(content_types=['audio', 'video', 'document', 'location', 'contact', 'sticker'])
def handle_unsupported(message):
    bot.reply_to(message, "Извините, пока я работаю только с изображениями🙁")

@bot.message_handler(content_types=['text'])
def get_information(message):
    if message.chat.type == 'private':
        if message.text == '📑Контакты':
            bot.send_message(message.chat.id,'У вас что-то не работает?Или есть предложения о сотрудничестве?Напишите нам!\nГуреев Кирилл:\n📱Telegram: t.me/Valer04ka1488\n🌐Вконтакте: vk.com/abchik1488\n🐙GitHub:\n')
            bot.send_message(message.chat.id,'Гоголев Виктор:\n📱Telegram: t.me/wa55up\n🌐Вконтакте: vk.com/yowa55up\n🐙GitHub: github.com/paradaise\n')
        elif message.text == '🔗Другое':
            bot.send_message(message.chat.id,'🚫В разработке,пока недоступно🚫')
        elif message.text == '💸Поддержать':
            bot.send_message(message.chat.id,'💵Вы можете поддержать наш проект,нажав кнопку ниже:', reply_markup = keyboard(donation_menu))
        elif message.text == '🫰Юмани':
            bot.send_message(message.chat.id,'🫰Вы можете поддержать Юмани по ссылке:\nhttps://yoomoney.ru/to/410013032669115')
        elif message.text == '💰СБП':
            bot.send_message(message.chat.id,'💰Вы можете поддержать CБП по ссылке:')
        elif message.text == '↩️Назад':
            bot.send_message(message.chat.id,'↩️Возвращаемся к основному меню', reply_markup = keyboard(main_menu))


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    img_path = 'img.jpg'
    with open(img_path, 'wb') as new_file:
        new_file.write(bot.download_file(bot.get_file(message.photo[-1].file_id).file_path))

        result_msg, result_img = crop_and_ocr(img_path)

        bot.reply_to(message, result_msg)
        if result_img is not None:
            bot.send_photo(message.chat.id, result_img)
    

# Запуск бота
bot.polling(none_stop=True)
