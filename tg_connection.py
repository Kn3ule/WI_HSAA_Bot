from inspect import Traceback
from traceback import TracebackException
from parso import parse
from dotenv import load_dotenv
import os
import logging
from info import *

from postgres import my_session, Student, Module, Lecture_infos, enrolement_table

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

#Methode zum Start des Bots
def start(update: Update, context: CallbackContext):
    #Überprüfen ob Student schon hinterlegt ist (Über telegram_id), wenn nicht wird dieser hinzugefügt
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

#Methode um Modulübersicht anzeigen zu lassen
def modules(update: Update, context: CallbackContext):
    #Alle verfügbaren Module werden ausgelesen und in einen String gepackt
    all_modules = my_session.query(Module)
    all_modules_string = '<b> Übersicht aller Module </b> \n'
    for module in all_modules:
        id = module.id
        name = module.module_name

        all_modules_string += f'{id} - {name} \n'

    #Module, welche der Student schon hinzugefügt hat werden abgefragt und in einen String gepackt
    my_modules = my_session.query(enrolement_table).join(Student).join(Module).filter(Student.telegram_id == update.message.from_user.id)
    my_modules_string = '\n \n <b> Meine Module: </b> \n'
    for module in my_modules:
        id = module.modules_id
        name = my_session.query(Module).filter(Module.id == id).first().module_name
        my_modules_string += f'{id} - {name} \n'


    return_string = (
        '<b>Hier kannst du deine Module konfigurieren:</b> \n'
        'Mit /add {id} kannst du neue Module für deinen Studenplan hinzufügen.\n'
        'Mit /delete {id} kannst du Module aus deinem Stundenplan löschen!\n \n \n'
    )

    #Return String wird zusammgesetzt und als Nachricht zurückgeben
    return_string =  return_string + all_modules_string + my_modules_string

    context.bot.send_message(chat_id=update.effective_chat.id, text=return_string, parse_mode = 'HTML')

#Methode um Module mit Studenten zu verknüpfen(Many-to-Many)
def add_module(update: Update, context: CallbackContext):
    student = my_session.query(Student).filter(Student.telegram_id == update.message.from_user.id).first()
    module = my_session.query(Module).filter(Module.id == update.message.text.split(' ')[1]).first()
    relation_exist = my_session.query(enrolement_table).join(Student).join(Module).filter((Student.telegram_id == update.message.from_user.id) & (Module.id == update.message.text.split(' ')[1])).first()
    try:
        if relation_exist != None:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Modul ist schon hinterlegt!", parse_mode = 'HTML')
        else:
            student.modules.append(
                module
            )
            
            my_session.commit()
            return_string = f'Das Modul: {module.module_name} wurde hinzugefügt!'

            context.bot.send_message(chat_id=update.effective_chat.id, text= return_string, parse_mode = 'HTML')
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text= "Modul nicht verfügbar. Bitte überprüfe deine Eingabe!", parse_mode = 'HTML')

def delete_module(update: Update, context: CallbackContext):
    student = my_session.query(Student).filter(Student.telegram_id == update.message.from_user.id).first()
    module = my_session.query(Module).filter(Module.id == update.message.text.split(' ')[1]).first()

    try:
        student.modules.remove(module)
        context.bot.send_message(chat_id=update.effective_chat.id, text= f"Modul: {module.module_name} wurde entfernt!", parse_mode = 'HTML')
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text= "Modul konnte nicht entfernt werden!", parse_mode = 'HTML')

    


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
    modules_handler = CommandHandler('modules', modules)
    addmodule_handler = CommandHandler('add', add_module)
    deletemodules_handler = CommandHandler('delete', delete_module)
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(modules_handler)
    dispatcher.add_handler(addmodule_handler)
    dispatcher.add_handler(deletemodules_handler)
    updater.start_polling()


if __name__ == '__main__':
    main()