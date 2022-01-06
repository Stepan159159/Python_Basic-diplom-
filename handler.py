from Loader import *
import rapidapi as logic
from data import data
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP


def location(message) -> None:
    bot.send_message(message.chat.id, "Сейчас поищем, подождите.")
    location_id = logic.get_location_id(message.text)
    keyboard = telebot.types.InlineKeyboardMarkup()
    for key, value in location_id.items():
        keyboard.add(telebot.types.InlineKeyboardButton(
            text=key, callback_data=value, copy_text_to_callback=True))
    bot.send_message(message.from_user.id, text="Уточните пожалуйста.",
                     reply_markup=keyboard)


def check_in_date_callendar(message):
    calendar, step = DetailedTelegramCalendar(calendar_id=1).build()
    bot.send_message(message.chat.id,
                     f"Выберите дату заезда в отель {LSTEP[step]}",
                     reply_markup=calendar)


def check_out_date_callendar(message):
    calendar, step = DetailedTelegramCalendar(calendar_id=2).build()
    bot.send_message(message.chat.id,
                     f"Выберите дату выселения из отеля. {LSTEP[step]}",
                     reply_markup=calendar)


def min_price_get(message) -> None:
    try:
        txt = message.text
        txt = "".joinn(filter(lambda x: x in "1234567890.", txt))
        if int(txt) < 0:
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
    data[str(message.chat.id)]["price_min"] = price_min
    bot.register_next_step_handler(message, max_price_get)


def max_price_get(message) -> None:
    try:
        txt = message.text
        txt = "".joinn(filter(lambda x: x in "1234567890.", txt))
        send = int(txt)
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
    data[str(message.chat.id)]["price_max"] = price_max
    check_in_date_callendar(message)

def hotels_list(message) -> None:
    bot.send_message(message.chat.id, "Город найден ищем отели в нём.")
    chat_id = str(message.chat.id)
    hotels = logic.get_search_hotels(data[chat_id]["town"],
                                     data[str(message.chat.id)][
                                         "check_in_date"],
                                     data[str(message.chat.id)][
                                         "check_out_date"],
                                     data[chat_id]["mode"],
                                     data[chat_id].get("price_min", 0),
                                     data[chat_id].get("price_max", 999999))
    bot.send_message(message.chat.id, f"Нашлось отелей: {len(hotels)}")
    markup = telebot.types.ReplyKeyboardMarkup()
    send_yes = telebot.types.KeyboardButton('Да')
    send_no = telebot.types.KeyboardButton('Нет')
    z = [send_yes, send_no]
    markup.row(*z)

    bot.send_message(message.chat.id, "Выводить фото?")

    bot.send_message(message.chat.id, "Выберите ответ на клавиатуре.",
                     reply_markup=markup)
    data[str(message.chat.id)]["basic"].set_hotels([A["name"] for A in hotels])
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
    data[str(message.chat.id)]["basic"].save_for_bd()
    for numbers_elem in range(number_hotels):
        send = hotels_list[numbers_elem]["name"]
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
        bot.send_message(message.chat.id, str(hotels_list[numbers_elem]\
                                              ["optimizedThumbUrls"]\
                                                  ["srpDesktop"]))
        bot.send_message(message.chat.id, "=" * 57)