import telegram_bot_calendar
from handler import check_in_date_callendar, check_out_date_callendar, \
    min_distance_get, hotels_list, location
from Loader import bot
from History import Users


@bot.message_handler(commands=['start', 'help'])
def menu(message):
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
    logs = Users.read(message.chat.id)
    for row in logs:
        bot.send_message(message.chat.id,row)


@bot.message_handler(commands=['highprice', 'bestdeal', 'lowprice'])
def get_text_messages(message) -> None:
    if message.text == '/highprice':
        mode = "PRICE_HIGHEST_FIRST"
    elif message.text == '/lowprice':
        mode = "PRICE"
    else:
        mode = "DISTANCE_FROM_LANDMARK"
    bot.send_message(message.chat.id, "Введите город.")
    Users(user_id=message.chat.id, command=message.text.replace("/", ""),
          mode=mode)
    bot.register_next_step_handler(message, location)


@bot.callback_query_handler(func=telegram_bot_calendar\
                            .DetailedTelegramCalendar.func(calendar_id=1))
def check_in_date(call):
    result, key, step = telegram_bot_calendar.DetailedTelegramCalendar(
        calendar_id=1).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите дату заезда в отель "
                              f"{telegram_bot_calendar.LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        Users.get_user(call.message.chat.id).check_in = result
        check_out_date_callendar(call.message)


@bot.callback_query_handler(func=telegram_bot_calendar\
                            .DetailedTelegramCalendar.func(calendar_id=2))
def check_out_date(call):
    result, key, step = telegram_bot_calendar.DetailedTelegramCalendar(
        calendar_id=2).process(
        call.data
    )
    if not result and key:
        bot.edit_message_text(f"Выберите дату выселения из отель "
                              f"{telegram_bot_calendar.LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        Users.get_user(call.message.chat.id).check_out = result
        hotels_list(call.message)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    usr = Users.get_user(call.message.chat.id)
    usr.city = call.data
    bot.send_message(call.message.chat.id, "Благодарю.")
    if Users.get_user(call.message.chat.id).mode == "DISTANCE_FROM_LANDMARK":
        bot.send_message(call.message.chat.id, "Введите минимальную дистанцию"
                                               "от центра города.")
        bot.register_next_step_handler(call.message, min_distance_get)
    else:
        check_in_date_callendar(call.message)


bot.polling(none_stop=True, interval=0)
