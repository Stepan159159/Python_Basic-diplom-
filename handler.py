from Loader import bot
import telebot
import rapidapi as logic
from History import Users
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP


def location(message) -> None:
    bot.send_message(message.chat.id, "Сейчас поищем, подождите.")
    location_id = logic.get_location_id(message.text)
    keyboard = telebot.types.InlineKeyboardMarkup()
    if len(location_id) == 0:
        bot.send_message(message.from_user.id, text=
        "К сожалению по данному запросу ничего не найдено.")
        return
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
    txt = message.text
    txt = "".join(filter(lambda x: x in "1234567890", txt))
    txt = txt if txt != "" else "0"
    price_min = int(txt)

    bot.send_message(message.chat.id, "Введите максимальную цену")
    Users.get_user(message.chat.id).price_min = price_min
    bot.register_next_step_handler(message, max_price_get)


def max_price_get(message) -> None:
    txt = message.text
    txt = "".join(filter(lambda x: x in "1234567890", txt))
    send = int(txt) if txt != "" else 999999
    if send > 999999:
        bot.send_message(message.chat.id, "Это слишком много ")
        bot.send_message(message.chat.id, "По этому установим на 999999.")
        price_max = 999999
    else:
        price_max = send
    Users.get_user(message.chat.id).price_max = price_max
    check_in_date_callendar(message)


def hotels_list(message) -> None:
    bot.send_message(message.chat.id, "Город найден ищем отели в нём.")
    chat_id = message.chat.id
    usr =  Users.get_user(chat_id)
    hotels = logic.get_search_hotels(usr.city,
                                     usr.check_in,
                                     usr.check_out,
                                     usr.mode,
                                     usr.price_min,
                                     usr.price_max)
    bot.send_message(message.chat.id, f"Нашлось отелей: {len(hotels)}")
    markup = telebot.types.ReplyKeyboardMarkup()
    send_yes = telebot.types.KeyboardButton('Да')
    send_no = telebot.types.KeyboardButton('Нет')
    z = [send_yes, send_no]
    markup.row(*z)

    bot.send_message(message.chat.id, "Выводить фото?")

    bot.send_message(message.chat.id, "Выберите ответ на клавиатуре.",
                     reply_markup=markup)
    usr.hotels = hotels
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
    txt = message.text
    txt = "".join(filter(lambda x: x in "1234567890", txt))
    if txt == "":
        bot.send_message(message.chat.id,
                         "Я не понял сколько вы имели в виду "
                         "по этому выведу 10.")
        number_photos = 10
    else:
        number_photos = int(txt)
        if number_photos > 10:
            bot.send_message(message.chat.id, "Больше 10 нельзя.")
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

    txt = message.text
    txt = "".join(filter(lambda x: x in "1234567890", txt))
    if txt != "":
        number_hotels = int(txt)
        if number_hotels > len(hotels_list):
            send = f"Максимум равен {len(hotels_list)}. По этому установим его."
            bot.send_message(message.chat.id, send)
            number_hotels = len(hotels_list)
    else:
        send = f"Я вас не понял по этому поставим {len(hotels_list)}"
        bot.send_message(message.chat.id, send)
        number_hotels = len(hotels_list)

    Users.get_user(message.chat.id).hotels_count = number_hotels
    send_result(message, hotels_list=hotels_list, number_photos=number_photos,
                number_hotels=number_hotels)


def send_result(message, hotels_list: list = None, number_photos: int = 0,
                number_hotels: int = 0) -> None:
    Users.get_user(message.chat.id).save()
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
        bot.send_message(message.chat.id, f'https://ru.hotels.com/ho'
                         f'{hotels_list[numbers_elem]["id"]}')
        bot.send_message(message.chat.id, "=" * 57)