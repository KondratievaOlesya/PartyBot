"""PartyBot main functional"""
import datetime as dt
import re
import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, \
    Filters, ConversationHandler
from telegram_bot_pagination import InlineKeyboardPaginator
from dotenv import dotenv_values

from partybot import kudago, tools

config = dotenv_values(".env")

MAX_MESSAGE_LEN = 1000
LOCATION, DATE, TIME, REQUEST = range(4)
SUPPORTED_CITY = ['москва']
request_data = {
    'city': '',
    'date': dt.datetime.min,
    'date_from': '',
    'date_to': ''
}


def start(update, _):
    """
    Send a message when the command /start is issued.

    :param telegram.Update update: Bot updater object
    :param telegram.ext.CallbackContext _:

    :return: int
    """

    update.message.reply_text(
        'Привет! Я - PartyBot.\n'
        'Для того, чтобы помочь тебе, мне необходима задать пару вопросов.\n'
        'Из какого ты города?'
    )
    return LOCATION


def check_location(city):
    """
    Check if bot support city

    :param string city: String with city name
    :return: bool
    """
    if city.lower() in SUPPORTED_CITY:
        return True
    return False


def location(update, _):
    """
    Process reply with city and continue dialog to date.

    :param telegram.Update update: Bot updater object
    :param telegram.ext.CallbackContext _:

    :return: int
    """

    city = update.message.text
    if check_location(city):
        request_data['city'] = city.lower()
        update.message.reply_text(
            f'Поиск будет производиться по городу {city.lower().capitalize()}'
        )
        data_variants = [['Сегодня', 'Завтра', 'Дата']]
        update.message.reply_text(
            'На какой день тебе интересны события?',
            reply_markup=ReplyKeyboardMarkup(data_variants, resize_keyboard=True),
        )
        return DATE

    allowed_city = tools.array_join(SUPPORTED_CITY, ',\n', lambda x: x.capitalize())
    update.message.reply_text(
        'Я не смог распознать город или этот горд не поддерживается! \n'
        f'Я поддерживаю следующий список городов:\n{allowed_city} \n'
        'Попробой ввести снова или закончи разговор вызвав команду /cancel'
    )
    return LOCATION


def date(update, _):
    """
    Process reply with date and continue dialog to time.

    :param telegram.Update update: Bot updater object
    :param telegram.ext.CallbackContext _:

    :return: int
    """

    answer = update.message.text
    if answer == 'Сегодня':
        req_date = dt.datetime.now()
    elif answer == 'Завтра':
        req_date = dt.datetime.now() + dt.timedelta(days=1)
    elif answer == 'Дата':
        update.message.reply_text(
            'Укажи дату в формате ДД.ММ \n',
            reply_markup=ReplyKeyboardRemove()
        )
        return DATE
    else:
        try:
            req_date = dt.datetime.strptime(answer, '%d.%m')
            req_date = req_date.replace(year=dt.datetime.today().year)
        except Exception:
            update.message.reply_text(
                'Я не понимаю формат. Укажи дату в формате ДД.ММ \n'
                'Либо закончи разговор вызвав команду /cancel'
            )
            return DATE
    request_data['date'] = req_date
    update.message.reply_text(
        f'Поиск на {req_date.strftime("%d.%m")}',
        reply_markup=ReplyKeyboardRemove()
    )
    time_variants = [['Утро', 'День', 'Вечер']]
    update.message.reply_text(
        'Укажи время, которое тебе интересно',
        reply_markup=ReplyKeyboardMarkup(time_variants, resize_keyboard=True)
    )
    return TIME


def get_hours_minutes(time_str):
    """
    Try to find hours an minutes in string

    :param time_str: string with :-separated time
    :return: hours,  minutes
    """

    minutes = '00'
    sep = time_str.find(':')
    if sep != -1:
        hours, minutes = time_str.split(':')
    else:
        hours = time_str
    return int(hours), int(minutes)


def extract_time(req_date, message):
    """
    Extract time from message to datetime

    :param dt.datetime.date req_date: Date to search events
    :param string message: Reply message

    :return: two dates - from and to if it is possible to parse, None otherwise
    """
    time_reg = r'[0-2]?[0-9](?:\:[0-5][0-9])?'
    time_regs = [
        rf'с {time_reg}$',
        rf'с {time_reg} до {time_reg}$',
        rf'до {time_reg}$',
        rf'{time_reg}[ ]*-[ ]*{time_reg}$',
        rf'{time_reg}$'
    ]
    matched = False
    req_from = req_date
    req_to = req_date
    for reg in time_regs:
        if re.fullmatch(reg, message) is not None:
            matched = True
            times = re.findall(time_reg, message)
            if len(times) == 2:
                from_h, from_m = get_hours_minutes(times[0])
                to_h, to_m = get_hours_minutes(times[1])
                req_from = req_date.replace(hour=from_h, minute=from_m)
                req_to = req_date.replace(hour=to_h, minute=to_m)
                if req_from > req_to:
                    req_to += dt.timedelta(days=1)
            elif len(times) == 1:
                if reg[:2] == 'до':
                    to_h, to_m = get_hours_minutes(times[0])
                    req_from = req_date.replace(hour=0, minute=0)
                    req_to = req_date.replace(hour=to_h, minute=to_m)

                    if to_h < 6:
                        req_to += dt.timedelta(days=1)
                else:
                    from_h, from_m = get_hours_minutes(times[0])
                    req_from = req_date.replace(hour=from_h, minute=from_m)
                    req_to = req_date.replace(hour=23, minute=59)
            break
    if matched:
        return req_from, req_to
    return None


def time(update, _):
    """
    Process reply with time and search complete request.

    :param telegram.Update update: Bot updater object
    :param telegram.ext.CallbackContext _:

    :return: int
    """

    mess = update.message.text
    req_time = request_data['date']
    if not isinstance(req_time, dt.datetime):
        raise ValueError('Date is not in correct format!')
    if mess == 'Утро':
        req_from = req_time.replace(hour=6, minute=0)
        req_to = req_time.replace(hour=12, minute=0)
    elif mess == 'День':
        req_from = req_time.replace(hour=12, minute=0)
        req_to = req_time.replace(hour=16, minute=0)
    elif mess == 'Вечер':
        req_from = req_time.replace(hour=16, minute=0)
        req_to = req_from + dt.timedelta(days=1)
        req_to = req_to.replace(hour=6, minute=0)
    else:
        res = extract_time(req_time, mess)
        if res is not None:
            req_from, req_to = res
        else:
            update.message.reply_text(
                'Я не смог понять время, попробуй ввести еще раз\n'
                'Либо закончи разговор вызвав команду /cancel'
            )
            return TIME
    request_data['date_from'] = req_from
    request_data['date_to'] = req_to
    update.message.reply_text(
        f'Поиск с {req_from.strftime("%d.%m %H:%M")} до {req_to.strftime("%d.%m %H:%M")}',
        reply_markup=ReplyKeyboardRemove()
    )
    show_events(update)
    return ConversationHandler.END


def to_pages(messages):
    """
    Sort messages in pages

    :param list messages: Messages to show
    :return: Pages to show
    :rtype: list
    """
    curr_len = 0
    num_pages = 0
    pages = []
    for message in messages:
        if (curr_len + len(message)) > MAX_MESSAGE_LEN or len(pages) == 0:
            num_pages += 1
            curr_len = len(message)
            pages.append(message)
        else:
            pages[num_pages - 1] += message
            curr_len += len(message)
    return pages


def show_events(update):
    """
    Shows events in pages

    :param telegram.Update update: Bot updater object
    :return: None
    """
    logging.info('Requests with %s.', request_data)
    kudago_events = kudago.send_request(request_data)
    pages = to_pages(kudago_events)
    send_character_page(update, pages)


def send_character_page(update, pages, page=1):
    """
    Create pages

    :param telegram.Update update: Bot updater object
    :param list pages: List with message to print on each page
    :param int page: Current number of page
    """

    paginator = InlineKeyboardPaginator(
        len(pages),
        current_page=page,
        data_pattern='character#{page}'
    )

    update.message.reply_text(
        pages[page - 1],
        reply_markup=paginator.markup,
        parse_mode='Markdown'
    )


def cancel(update, _):
    """
    Stop bot and send a message when the command /cancel is issued.

    :param telegram.Update update: Bot updater object
    :param telegram.ext.CallbackContext _:

    :return: int
    """
    update.message.reply_text(
        'Работа бота приостановленна. Для начала введите /start'
    )

    return ConversationHandler.END


def help_command(update, _):
    """
    Send a message when the command /help is issued.

    :param telegram.Update update: Bot updater object
    :param telegram.ext.CallbackContext _:

    :return: None
    """
    update.message.reply_text('''Бот понимает следующие команды:
    /start - Начало работы бота
    /cancel - Остановить работу бота
    /help - Вывести это сообщение''')


def main():
    """
    Start the bot.
    """
    logging.basicConfig(
        filename=config['LOG_FILE'],
        encoding='utf-8',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s:%(message)s'
    )

    updater = Updater(config['TOKEN'])
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LOCATION: [MessageHandler(Filters.text & ~Filters.command, location)],
            DATE: [MessageHandler(Filters.text & ~Filters.command, date)],
            TIME: [MessageHandler(Filters.text & ~Filters.command, time)],
            REQUEST: []
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
