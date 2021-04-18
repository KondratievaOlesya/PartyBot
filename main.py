import telebot

bot = telebot.TeleBot('')


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == "/start":
        bot.send_message(message.from_user.id, "Привет, я помогу тебе найти тусовки. Ответь на пару вопросов")
        bot.send_message(message.from_user.id, 'На какую дату ты ищешь события?')
        bot.register_next_step_handler(message, get_date)
    elif message.text == "/help":
        # @TODO Help page
        bot.send_message(message.from_user.id, "Напиши привет")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")


def get_date(message):
    # @TODO Check data >= today
    print(message)
    bot.send_message(message.from_user.id, 'На какую дату ты ищешь события?')


bot.polling(none_stop=True, interval=0)
