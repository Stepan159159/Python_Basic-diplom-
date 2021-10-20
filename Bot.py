import telebot
import main as logic
import os
bot = telebot.TeleBot('2049973347:AAHg20A0RHPFbDW1MVeiI3Z5MOnoqvtZslM')


@bot.message_handler(commands=['start', 'help'])
def menu(message):
    logic.Log.write(message.chat.id, message.text)
    menu_1 = "1. Узнать топ самых дешёвых отелей в городе (команда /lowprice)."
    menu_2 = "2. Узнать топ самых дорогих отелей в городе (команда /highprice)."
    menu_3 = "3. Узнать топ отелей, наиболее подходящих по цене и " \
        "расположению от центра""(самые дешёвые и находятся " \
             "ближе всего к центру) (команда /bestdeal)."
    menu_4 = "4. Узнать историю поиска отелей (команда /history)"
    bot.send_message(message.chat.id, menu_1)
    bot.send_message(message.chat.id, menu_2)
    bot.send_message(message.chat.id, menu_3)
    bot.send_message(message.chat.id, menu_4)


@bot.message_handler(commands=['history'])
def history(message) -> None:
    for text in logic.Log.read(message.chat.id):
        bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['highprice'])
def get_text_messages(message) -> None:
    logic.Log.write(message.chat.id, message.text)
    bot.send_message(message.chat.id, "Введите город!")
    bot.register_next_step_handler(message, location,
                                   mode="PRICE_HIGHEST_FIRST")


@bot.message_handler(commands=['lowprice'])
def get_text_messages(message) -> None:
    logic.Log.write(message.chat.id, message.text)
    bot.send_message(message.chat.id, "Введите город!")
    bot.register_next_step_handler(message, location, mode="PRICE")


@bot.message_handler(commands=['bestdeal'])
def get_text_messages(message) -> None:
    logic.Log.write(message.chat.id, message.text)
    bot.send_message(message.chat.id, "Введите город!")
    bot.register_next_step_handler(message, location,
                                   mode="DISTANCE_FROM_LANDMARK")


def location(message, mode: str = "PRICE") -> None:
    bot.send_message(message.chat.id, "Сейчас поищем, подождите.")
    location_id = logic.get_location_id(message.text)
    if location_id is None:
        bot.send_message(message.chat.id, "Данный город не найден повторите "
                                          "попытку")
        return
    if mode == "DISTANCE_FROM_LANDMARK":
        bot.send_message(message.chat.id, "Укажите минимальную цену.")
        bot.register_next_step_handler(message, min_price_get, mode,
                                       location_id)
    else:
        hotels_list(message, location_id, mode)


def min_price_get(message, mode: str, location_id: str) -> None:
    try:
        if int(message.text) < 0:
            bot.send_message(message.chat.id, "Вам не будут платить за комнату!")
            bot.send_message(message.chat.id, "По этому установим на 0.")
            price_min = 0
        else:
            price_min = int(message.text)
    except Exception:
        bot.send_message(message.chat.id, "Я вас не понял ")
        bot.send_message(message.chat.id, "По этому установим на 0.")
        price_min = 0
    bot.send_message(message.chat.id, "Введите максимальную цену")
    bot.register_next_step_handler(message, max_price_get, mode,
                                   price_min, location_id)


def max_price_get(message, mode: str, price_min: int, location_id: str) -> None:
    try:
        send = int(message.text)
        if send < 0:
            bot.send_message(message.chat.id, "Вам не будут платить за комнату!")
            bot.send_message(message.chat.id, "По этому установим на 999999.")
            price_max = 999999
        elif send > 999999:
            bot.send_message(message.chat.id, "Это слишком много ")
            bot.send_message(message.chat.id, "По этому установим на 999999.")
            price_max = 999999
        else:
            price_max = send

    except Exception:
        bot.send_message(message.chat.id, "Я вас не понял ")
        bot.send_message(message.chat.id, "По этому установим на 999999.")
        price_max = 999999
    hotels_list(message, location_id, mode, price_min=price_min,
                price_max=price_max)


def hotels_list(message, location_id, mode: str, price_min: int = 0,
                price_max: int = 999999) -> None:
    bot.send_message(message.chat.id, "Город найден ищем отели в нём.")
    hotels = logic.get_search_hotels(location_id, mode, price_min=price_min,
                                     price_max=price_max)

    bot.send_message(message.chat.id, f"Нашлось отелей: {len(hotels)}")

    markup = telebot.types.ReplyKeyboardMarkup()
    send_yes = telebot.types.KeyboardButton('Да')
    send_no = telebot.types.KeyboardButton('Нет')
    z = [send_yes, send_no]
    markup.row(*z)

    bot.send_message(message.chat.id, "Выводить фото?")

    bot.send_message(message.chat.id, "Выберите ответ на клавиатуре",
                     reply_markup=markup)
    bot.register_next_step_handler(message, picture, hotels_list=hotels)


def picture(message, hotels_list: list[dict] = None) -> None:
    def oh_no():
        bot.send_message(message.chat.id, "О скольки отелях вам рассказать?")
        bot.send_message(message.chat.id, f"Максимум равен {len(hotels_list)}")
        bot.send_message(message.chat.id, "(напишите количество цифрами.)")
        bot.register_next_step_handler(message, set_max_hotels,
                                       hotels_list=hotels_list,
                                       number_photos=0)

    mark = telebot.types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, "Хорошо", reply_markup=mark)
    if message.text.lower() == "да":
        bot.send_message(message.chat.id, "а сколько?")
        bot.send_message(message.chat.id, "(максимум 10)")
        bot.register_next_step_handler(message, set_max_photo,
                                       hotels_list=hotels_list)
    elif message.text.lower() == "нет":
        oh_no()
    else:
        bot.send_message(message.chat.id, "Я не понял, что вы имели в виду")
        bot.send_message(message.chat.id, "но пусть это будет нет.")
        oh_no()


def set_max_photo(message, hotels_list: list = None):
    try:
        number_photos = int(message.text)
        if number_photos > 10:
            bot.send_message(message.chat.id, "Больше 10 нельзя.")
            number_photos = 10
    except Exception:
        bot.send_message(message.chat.id,
                         "Я не понял сколько вы имели в виду "
                         "по этому выведу 10.")
        number_photos = 10

    bot.send_message(message.chat.id, "О скольки отелях вам рассказать?")
    send = f"Максимум равен {len(hotels_list)}"
    bot.send_message(message.chat.id, send)
    bot.send_message(message.chat.id, "(напишите количество цифрами)")
    bot.register_next_step_handler(message, set_max_hotels,
                                   hotels_list=hotels_list,
                                   number_photos=number_photos)


def set_max_hotels(message, hotels_list: list = None, number_photos: int = 0)\
        -> None:
    try:
        number_hotels = int(message.text)
        if number_hotels > len(hotels_list):
            send = f"Максимум равен {len(hotels_list)}. По этому установим его."
            bot.send_message(message.chat.id, send)
            number_hotels = len(hotels_list)
    except Exception:
        send = f"Я вас не понял по этому поставим {len(hotels_list)}"
        bot.send_message(message.chat.id, send)
        number_hotels = len(hotels_list)

    send_result(message, hotels_list=hotels_list, number_photos=number_photos,
                number_hotels=number_hotels)


def send_result(message, hotels_list: list = None, number_photos: int = 0,
                number_hotels: int = 0) -> None:
    for numbers_elem in range(number_hotels):
        send = hotels_list[numbers_elem]["name"]
        logic.Log.write(message.chat.id, send)
        bot.send_message(message.chat.id, send)

        send = hotels_list[numbers_elem]["address"]["streetAddress"]
        bot.send_message(message.chat.id, send)

        send = str(hotels_list[numbers_elem]["landmarks"][0]["label"]) + " " +\
               str(hotels_list[numbers_elem]["landmarks"][0]["distance"])
        bot.send_message(message.chat.id, send)

        send = "Цена номера на одного равна " +\
               str(hotels_list[numbers_elem]["ratePlan"]["price"]
                   ["exactCurrent"])
        bot.send_message(message.chat.id, send)
        if number_photos > 0:
            photos = logic.get_photo(hotels_list[numbers_elem]["id"])
            for photo_index in range(number_photos):
                bot.send_photo(message.chat.id, photos[photo_index])
        bot.send_message(message.chat.id, "=" * 57)


bot.polling(none_stop=True, interval=0)
