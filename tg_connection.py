from inspect import Traceback
from traceback import TracebackException
from parso import parse
from dotenv import load_dotenv
import os
import logging
from info import *

from postgres import my_session, Student

from telegram import Update, ParseMode
import telegram
from telegram.ext import CallbackContext,Updater,CommandHandler,MessageHandler, Filters
#set up and use .env File for the API-Token
load_dotenv()
token = os.getenv("TELEGRAM_TOKEN")

#set up log
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    try:
        new_student = Student(telegram_id = update.message.from_user.id, first_name= update.message.from_user.first_name, last_name= update.message.from_user.last_name)
        my_session.add(new_student)
        my_session.commit()
    except Exception as err:
        logger.error(err)
    greeting = (
        f'Hallo {update.message.from_user.first_name} {update.message.from_user.last_name}!\n'
        f'Ich bin der Informationsbot des Studiengangs Wirtschaftsinformatik der Hochschule Aalen\n'
        f'Falls du deine Module konfigurieren und hinterlegen möchtest, um sie später abzufragen, starte den Prozess mit: /modules \n'
        f'Um Andere Informationen zu erhalten Frag mich einfach!'
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=greeting)

def echo(update: Update, context: CallbackContext):
    if update.message.text == "aktuelles":
        output = get_news()
    else:
        output = get_downloads(update.message.text)
    print(context._user_id_and_data)
    #context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=output, parse_mode='HTML')


def main():

    #create an Updater Object
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(echo_handler)
    updater.start_polling()


if __name__ == '__main__':
    main()