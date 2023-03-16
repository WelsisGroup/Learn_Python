import re
import telebot
from telebot import util
from datetime import datetime
import DB, req_to_site
from auth_data import TOKEN
from telegram_bot_calendar import DetailedTelegramCalendar
from loguru import logger

bot = telebot.TeleBot(f'{TOKEN}', parse_mode=None)
LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}
user_input_dct = {}
dt_now = datetime.now()

print('Бот запущен') #Отображения готовности работы бота


''' СПИСОК КОМАНД БОТА '''


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    DB.create_table_in_db_by_userid(message.chat.id)
    with open(file='logs_command.log', mode='a', encoding='UTF-8') as logfile:
        logfile.write(f'\n{dt_now}|Пользователь с id {message.chat.id} ввел команду start/help')
    logger.info(f'Пользователь с id {message.chat.id} ввел команду start/help')
    bot.reply_to(message, 'Привет. Я бот-помощник компании Too Easy Travel.\n'
                          'Помогу тебе с выбором отелей.\n'
                          '📉 /lowprice - топ самых дешевых отелей в городе\n'
                          '📈 /highprice - топ самых дорогих отелей в городе\n'
                          '🔝 /bestdeal - топ отелей, подходящих по цене и расположению от центра\n'
                          '📒 /history - узнать свою историю поиска отелей\n'
                          '🔧 /help - мои команды')


@bot.message_handler(func=lambda message:message.text not in
                                         ['/lowprice',
                                          '/bestdeal',
                                          '/highprice',
                                          '/history',
                                          '/help',
                                          '/start'])
def answer_to_some_text(message):
    bot.reply_to(message, 'Такой команды у меня нет. Попробуй вот эти:'
                          '📉 /lowprice - топ самых дешевых отелей в городе\n'
                          '📈 /highprice - топ самых дорогих отелей в городе\n'
                          '🔝 /bestdeal - топ отелей, подходящих по цене и расположению от центра\n'
                          '📒 /history - узнать свою историю поиска отелей\n'
                          '🔧 /help - мои команды')


@bot.message_handler(commands='lowprice')
def send_lowprice(message):
    with open(file='logs_command.log', mode='a', encoding='UTF-8') as logfile:
        logfile.write(f'\n{dt_now}|Пользователь с id {message.chat.id} ввел команду lowprice')
    logger.info(f'Пользователь с id {message.chat.id} ввел команду lowprice')
    user_input_dct['command_flag'] = 'lowprice'
    first_step(message)


@bot.message_handler(commands='highprice')
def send_highprice(message):
    with open(file='logs_command.log', mode='a', encoding='UTF-8') as logfile:
        logfile.write(f'\n{dt_now}|Пользователь с id {message.chat.id} ввел команду hihgprice')
    logger.info(f'Пользователь с id {message.chat.id} ввел команду hihgprice')
    user_input_dct['command_flag'] = 'highprice'
    first_step(message)


@bot.message_handler(commands='bestdeal')
def send_bestdeal(message):
    with open(file='logs_command.log', mode='a', encoding='UTF-8') as logfile:
        logfile.write(f'\n{dt_now}|Пользователь с id {message.chat.id} ввел команду bestdeal')
    logger.info(f'Пользователь с id {message.chat.id} ввел команду bestdeal')
    user_input_dct['command_flag'] = 'bestdeal'
    first_step_bestdeal(message)


@bot.message_handler(commands='history')
def send_history(message):
    with open(file='logs_command.log', mode='a', encoding='UTF-8') as logfile:
        logfile.write(f'\n{dt_now}|Пользователь с id {message.chat.id} ввел команду history')
    logger.info(f'Пользователь с id {message.chat.id} ввел команду history')
    bot.send_message(message.chat.id, message.chat.id)
    history_for_send = DB.print_db_info(message.chat.id)
    for i_elem in history_for_send:
        bot.send_message(message.chat.id, f'Дата запроса: {i_elem[0]}')
        splitted_text = util.smart_split(i_elem[1], chars_per_string=3000)
        for i_text in splitted_text:
            bot.send_message(message.chat.id, i_text)


''' ОСНОВНОЙ ФУНКЦИОНАЛ БОТА'''

''' Функции для получения информации от пользователя '''


def first_step(message):
    city = 'Введите город поиска: '
    bot.send_message(message.chat.id, city)
    bot.register_next_step_handler(message, city_reg)


def city_reg(message):
    user_input_dct['date_flag'] = False
    user_input_dct['date_range'] = []
    user_input_dct['city'] = message.text
    check_in = 'Введите дату заезда: '
    bot.send_message(message.chat.id, check_in)
    input_by_calend_buttons(message)
    while not user_input_dct['date_flag']:
        pass
    check_in_f(message)


def check_in_f(message):
    user_input_dct['date_flag'] = False
    check_out = 'Введите дату выезда: '
    bot.send_message(message.chat.id, check_out)
    input_by_calend_buttons(message)
    while not user_input_dct['date_flag']:
        pass
    check_out_f(message)


def check_out_f(message):
    user_input_dct['date_difference'] = (user_input_dct['date_range'][1] - user_input_dct['date_range'][0]).days

    num_hotels = 'Количество отелей для вывода (лимит: 15 отелей): '
    bot.send_message(message.chat.id, num_hotels)
    bot.register_next_step_handler(message, num_hotels_f)


def num_hotels_f(message):
    if message.text.isdigit():
        if int(message.text) > 15:
            bot.send_message(message.chat.id, 'Слишком большая цифра. Мой лимит 15. Столько и выведу.')
            user_input_dct['num_hotels'] = 15
        elif int(message.text) <= 15:
            user_input_dct['num_hotels'] = int(message.text)

    send_photo = 'Будем загружать фото каждого отеля? (Да/Нет): '
    bot.send_message(message.chat.id, send_photo)
    bot.register_next_step_handler(message, send_photo_f)


def send_photo_f(message):
    if message.text.lower() == 'да':
        user_input_dct['send_photo'] = True
        bot.send_message(message.chat.id, 'Загружаю фото отелей')
        num_hot_photo = 'Введите количество фото отеля (лимит: 15 фото): '
        bot.send_message(message.chat.id, num_hot_photo)
        bot.register_next_step_handler(message, num_hot_photo_f)
    elif message.text.lower() == 'нет':
        user_input_dct['send_photo'] = False
        bot.send_message(message.chat.id, 'Не буду загружать фото отеля.')
        req_and_answer(message)
    else:
        user_input_dct['send_photo'] = False
        bot.send_message(message.chat.id, 'Ваша команда не распознана.\n'
                                          'Наверное, вы не хотели загружать фото отелей.')
        num_hotels_f(message)


def num_hot_photo_f(message):
    if int(message.text) > 15:
        bot.send_message(message.chat.id, 'Слишком большая цифра. Мой лимит 15. Столько и выведу.')
        user_input_dct['num_hot_photo'] = 15
    else:
        user_input_dct['num_hot_photo'] = int(message.text)
        req_and_answer(message)


def req_and_answer(message):
    ''' API запросы для получения информации о выбранных отелях '''

    bot.send_message(message.chat.id, 'Ищу отели по вашему запросу\n'
                                      'Скорость моего ответа зависит от вашего выбора.')
    check_in = datetime.strftime(user_input_dct['date_range'][0], '%Y-%m-%d')
    check_out = datetime.strftime(user_input_dct['date_range'][1], '%Y-%m-%d')
    destination_id = req_to_site.fst_request_for_destination_id(user_input_dct['city'])
    hotels_lst = req_to_site.sec_request_for_hotel_info(destination_id=destination_id,
                                                        check_in=check_in,
                                                        check_out=check_out)
    sort_results(message, hotels_lst)


def sort_results(message, hotels_lst):
    ''' Функция сортировки результатов поиска . '''

    if user_input_dct['command_flag'] == 'lowprice':
        hotels_lst = sorted(hotels_lst, key=lambda i_hotel: i_hotel['ratePlan']['price']['current'])
    elif user_input_dct['command_flag'] == 'highprice':
        hotels_lst = sorted(hotels_lst, key=lambda i_hotel: i_hotel['ratePlan']['price']['current'], reverse=True)
    elif user_input_dct['command_flag'] == 'bestdeal':
        hotels_lst = list(filter(bestdeal_func, hotels_lst))
        if len(hotels_lst) == 0:   
            bot.send_message(message.chat.id, 'По вашему запросу ничего не найдено.')
            return
    print_info(message, hotels_lst)


def bestdeal_func(i_hotel):
    ''' Функция сортировки результатов для bestdeal '''

    cur_price = int(i_hotel['ratePlan']['price']['exactCurrent'])
    cur_distance = float(i_hotel['landmarks'][0]['distance'].split()[0])
    if (user_input_dct['min_price'] <= cur_price <= user_input_dct['max_price']) \
            and user_input_dct['min_distance'] <= cur_distance <= user_input_dct['max_distance']:
        return i_hotel


def print_info(message, hotels_lst):
    ''' Функция для конечного вывода информации об отелях'''

    its_already_history = 'Город поиска отелей: '
    bot.send_message(message.chat.id, f'{user_input_dct["city"]}')
    its_already_history = ''.join([its_already_history, f'{user_input_dct["city"]}', '\n'])

    for i_num in range(user_input_dct['num_hotels']):
        print_hotel_count = f'====={i_num + 1} ОТЕЛЬ====='
        bot.send_message(message.chat.id, print_hotel_count)
        its_already_history = ''.join([its_already_history, print_hotel_count, '\n'])

        answer_to_user = f'\nНазвание отеля: ' \
                         f'{hotels_lst[i_num].get("name")}\n' \
                         f'Рейтинг отеля: ' \
                         f'{hotels_lst[i_num].get("starRating")} звёзд\n' \
                         f'Адрес отеля: ' \
                         f'{hotels_lst[i_num]["address"].get("streetAddress")}, ' \
                         f'{hotels_lst[i_num]["address"].get("locality")}, ' \
                         f'{hotels_lst[i_num]["address"].get("postalCode")}, ' \
                         f'{hotels_lst[i_num]["address"].get("region")}, ' \
                         f'{hotels_lst[i_num]["address"].get("countryName")}\n' \
                         f'Расстояние до центра города: ' \
                         f'{hotels_lst[i_num]["landmarks"][0].get("distance")}\n' \
                         f'Средняя цена за сутки: ' \
                         f'{hotels_lst[i_num]["ratePlan"]["price"].get("current")}\n' \
                         f'Суммарная стоимость проживания за {user_input_dct["date_difference"]} дней: ' \
                         f'{int(hotels_lst[i_num]["ratePlan"]["price"].get("exactCurrent")) * user_input_dct["date_difference"]}$\n' \
                         f'URL адрес отеля: ' \
                         f'{hotels_lst[i_num].get("urls")}\n'
        bot.send_message(message.chat.id, answer_to_user)
        its_already_history = ''.join([its_already_history, answer_to_user, '\n'])

        if user_input_dct['send_photo']:
            photo_url_lst = req_to_site.third_request_for_hotels_photo(
                hotel_id=hotels_lst[i_num]['id'], num_hot_photo=user_input_dct['num_hot_photo']
            )
            its_already_history = ''.join([its_already_history, 'Ссылки на фото отелей: ', '\n'])
            for i_photo_url in photo_url_lst:
                bot.send_message(message.chat.id, i_photo_url)
                its_already_history = ''.join([its_already_history, i_photo_url, '\n'])
    else:
        bot.send_message(message.chat.id, 'Вывод окончен. Надеюсь, вы нашли то, что вам нужно!')
    DB.add_data_to_db(message.chat.id, its_already_history)


''' Дополнительный функционал команды bestdeal'''


def first_step_bestdeal(message):
    input_text = 'Введите минимальную цену отеля [$]'
    bot.send_message(message.chat.id, input_text)
    bot.register_next_step_handler(message, max_price_f)


def max_price_f(message):
    users_price = re.findall(r'\d+', message.text)
    if len(users_price) == 2:
        users_price = float('.'.join([users_price[0], users_price[1]]))
    elif len(users_price) == 1:
        users_price = float(users_price[0])
    user_input_dct['min_price'] = users_price
    input_text = 'Введите максимальную цену отеля [$]'
    bot.send_message(message.chat.id, input_text)
    bot.register_next_step_handler(message, min_distance_f)


def min_distance_f(message):
    users_price = re.findall(r'\d+', message.text)
    if len(users_price) == 2:
        users_price = float('.'.join([users_price[0], users_price[1]]))
    elif len(users_price) == 1:
        users_price = float(users_price[0])
    user_input_dct['max_price'] = users_price
    input_text = 'Введите минимальное расстояние от отеля до центра города [метр]'
    bot.send_message(message.chat.id, input_text)
    bot.register_next_step_handler(message, max_distance_f)


def max_distance_f(message):
    users_distance = float(re.search(r'\d+', message.text).group(0))
    user_input_dct['min_distance'] = round(users_distance / 1609.34, 2)
    input_text = 'Введите максимальное расстояние от отеля до центра города [метр]'
    bot.send_message(message.chat.id, input_text)
    bot.register_next_step_handler(message, from_bestdeal_to_common_struct)


def from_bestdeal_to_common_struct(message):
    users_distance = float(re.search(r'\d+', message.text).group(0))
    user_input_dct['max_distance'] = round(users_distance / 1609.34, 2)
    first_step(message)


''' Функция для ввода даты при помощи календаря '''


def input_by_calend_buttons(message):
    ''' Функция для создания календаря '''
    calendar, step = DetailedTelegramCalendar(locale='ru').build()
    bot.send_message(message.chat.id,
                     f"Календарь для выбора даты: {LSTEP[step]}",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal1(c):
    ''' Функция обработки действий пользователя при вводе даты '''
    result, key, step = DetailedTelegramCalendar(locale='ru').process(c.data)
    if not result and key:
        bot.edit_message_text(f"Выберите: {LSTEP[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        user_input_dct['date_flag'] = True
        user_input_dct['date_range'].append(result)
        bot.edit_message_text(f"Ваш выбор: {result} ",
                              c.message.chat.id,
                              c.message.message_id)


bot.infinity_polling() #Завершение работы бота
