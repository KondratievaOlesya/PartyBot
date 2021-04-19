from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import dotenv_values

config = dotenv_values(".env")


def start(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Привет! Ответь на пару вопросов')


def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def main() -> None:
    """Start the bot."""
    updater = Updater(config['TOKEN'])
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
