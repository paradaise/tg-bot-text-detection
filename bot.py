import telebot
from telebot import types
from image_processing import crop_and_ocr
from conf import TOKEN

bot = telebot.TeleBot(TOKEN)

main_menu = ('📑Контакты','🔗Другое','💸Поддержать')
donation_menu = ('🫰Юмани','↩️Назад')

def keyboard(menu):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    info = types.KeyboardButton(menu[0])
    other = types.KeyboardButton(menu[1])
    donation = types.KeyboardButton(menu[2])
    markup.add(info,other,donation)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    bot.reply_to(message, f"📸Привет,<b>{name},</b> я ищу текст на баннерах!\nОтправь фотографию и проверь!",reply_markup = keyboard(main_menu),parse_mode = "html")

@bot.message_handler(content_types=['audio', 'video', 'document', 'location', 'contact', 'sticker'])
def handle_unsupported(message):
    bot.reply_to(message, "Извините, пока я работаю только с изображениями🙁.Скоро будет обработка видео!",parse_mode="html")

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
        elif message.text == '↩️Назад':
            bot.send_message(message.chat.id,'↩️Возвращаемся к основному меню', reply_markup = keyboard(main_menu))

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    img_path = 'img.jpg'
    with open(img_path, 'wb') as new_file:
        new_file.write(bot.download_file(bot.get_file(message.photo[-1].file_id).file_path))

        result_msg, result_img = crop_and_ocr(img_path)


        bot.reply_to(message, result_msg,parse_mode="html")

        if result_img is not None:
            for img in result_img:
                bot.send_photo(message.chat.id, img)

# Запуск бота
bot.polling(none_stop=True)
