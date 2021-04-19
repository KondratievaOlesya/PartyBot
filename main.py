from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from dotenv import dotenv_values
import datetime as dt
from datetime import datetime
import tools

config = dotenv_values(".env")

LOCATION, DATE, TIME = range(3)
SUPPORTED_CITY = ['москва']


def start(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text(
        'Привет! Я - PartyBot.\n'
        'Для того, чтобы помочь тебе, мне необходима задать пару вопросов.\n'
        'Из какого ты города?'
    )
    return LOCATION


def check_location(city):
    if city.lower() in SUPPORTED_CITY:
        return True
    return False


def location(update: Update, _: CallbackContext) -> int:
    city = update.message.text
    if check_location(city):
        update.message.reply_text(
            f'Поиск будет производиться по городу {city.lower().capitalize()}'
        )
        data_variants = [['Сегодня', 'Завтра', 'Дата']]
        update.message.reply_text(
            'На какой день тебе интересны события?',
            reply_markup=ReplyKeyboardMarkup(data_variants, one_time_keyboard=True, resize_keyboard=True),
        )
        return DATE
    else:
        allowed_city = tools.array_join(SUPPORTED_CITY, ',\n', lambda x: x.capitalize())
        update.message.reply_text(
            'Я не смог распознать город или этот горд не поддерживается! \n'
            f'Я поддерживаю следующий список городов:\n{allowed_city} \n'
            'Попробой ввести снова или закончи разговор вызвав команду /cancel'
        )
        return LOCATION


def date(update: Update, _: CallbackContext) -> int:
    answer = update.message.text
    if answer == 'Сегодня':
        req_date = datetime.now()
    elif answer == 'Завтра':
        req_date = datetime.now() + dt.timedelta(days=1)
    elif answer == 'Дата':
        update.message.reply_text(
            'Укажи дату в формате ДД.ММ \n',
            reply_markup=ReplyKeyboardRemove()
        )
        return DATE
    else:
        try:
            req_date = datetime.strptime(answer, '%d.%m')
        except Exception as e:
            update.message.reply_text(
                'Я не понимаю формат. Укажи дату в формате ДД.ММ \n'
                'Либо закончи разговор вызвав команду /cancel',
                reply_markup=ReplyKeyboardRemove()
            )
            return DATE

    update.message.reply_text(
        f'Поиск на {req_date.strftime("%d.%m")}',
        reply_markup=ReplyKeyboardRemove()
    )
    update.message.reply_text(f'Укажи время, которое тебе интересно')
    return TIME


def time(update: Update, _: CallbackContext) -> int:
    return ConversationHandler.END


def cancel(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    update.message.reply_text(
        'Работа бота приостановленна. Для начала введите /start'
    )

    return ConversationHandler.END


def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def main() -> None:
    """Start the bot."""
    updater = Updater(config['TOKEN'])
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LOCATION: [MessageHandler(Filters.text & ~Filters.command, location)],
            DATE: [MessageHandler(Filters.text & ~Filters.command, date)],
            TIME: [MessageHandler(Filters.text & ~Filters.command, time)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
