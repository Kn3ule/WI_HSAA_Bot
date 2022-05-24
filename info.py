from datetime import date, timedelta
from nlp import preprocess
from bs4 import BeautifulSoup
import feedparser
import ssl
from postgres import *
from telegram import Update
import requests

hsaa = "www.hs-aalen.de"
basic_url = "https://www.hs-aalen.de/de/courses/39"
downloads = f"{basic_url}/downloads"
news = f"{basic_url}/news"


def get_downloads(input):
    page = requests.get(downloads)
    soup = BeautifulSoup(page.text, 'html.parser')

    panel = soup.find_all('div',class_='panel')

    try:
        for p in panel:
            if p.find('div', text=input) != None:
                head = p.find('div', text=input)
                data = p.find_all('div', class_='paragraph')


        heading = f'<b>  {str(head.get_text())} </b> \n'
        output = [heading]
        for d in data:
            
            text = str(d.get_text())
            if d.find('a') != None:
                link = hsaa + str(d.find('a').get('href'))
                link_text = str(d.find('a').getText())
                output.append(f'{text} \n <a href="{link}"> {link_text} </a> \n')
            else:
                output.append(f'{text} \n')
    except Exception:
        output = ["Ich konnte zu diesem Thema nichts finden"]

    return output

def get_infos(input):
    download_page = requests.get(downloads)
    download_soup = BeautifulSoup(download_page.text, 'html.parser')
    
    info_page = requests.get(f'{basic_url}/study')
    info_soup = BeautifulSoup(info_page.text, 'html.parser')
    info_panel = info_soup.find_all('div',class_='panel')

    output = []

    for p in info_panel:
        if p.find('div', text=input) != None:
            head = p.find('div', text=input)
            data = p.find_all('div', class_='paragraph')

            output.append(f'<b>  {str(head.get_text())} </b> \n')
            for d in data:
                text = str(d.get_text())
                output.append(f'{text} \n')


    download_panel = download_soup.find_all('div',class_='panel')

    if input == 'Anerkennungen': input = 'Antrag auf Leistungsanerkennung'

    for p in download_panel:
        if p.find('div', text=input) != None:
            head = p.find('div', text=input)
            data = p.find_all('div', class_='paragraph')

            for d in data:
                text = str(d.get_text())
                if d.find('a') != None:
                    link = hsaa + str(d.find('a').get('href'))
                    link_text = str(d.find('a').getText())
                    output.append(f'{text} \n <a href="{link}"> {link_text} </a> \n')
                else:
                    output.append(f'{text} \n')

    return output

def get_news():
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context
    feed = feedparser.parse(f'{basic_url}/infos.rss')

    #check if 
    if len(feed.entries) == 0:
        return 'Keine Neuigkeiten im Studiengang Wirtschaftsinformatik'


    output = [f'<b>  Neues im Studiengang Wirtschaftsinformatik: </b> \n\n']
    for e in feed.entries:
        title = f'{e.title}\n'

        output.append(f'{title}\n')

    output.append(f'mehr sehen: {basic_url}/news')
    
    return output

def get_date(input):
    input = input.lower()
    monday = date.today() + timedelta(-(date.today().weekday()))

    if 'heute' in input:
            
        dates = {
            'startdate': date.today(),
            'enddate' : (date.today() + timedelta(1))
            }

        return dates
    elif 'morgen' in input:
        dates = {
            'startdate': (date.today() + timedelta(1)),
            'enddate' : (date.today() + timedelta(2))
            }

        return dates

    elif 'diese woche' in input:
        dates = {
            'startdate': monday,
            'enddate' : (monday + timedelta(7))
            }

        return dates

    else:
        dates = {
            'startdate': monday,
            'enddate' : (monday + timedelta(7))
            }

        return dates

def get_lecture_info(tag, input, user_id):

    #get start- and enddate for filtering the lecture dates searched
    startdate = get_date(input)["startdate"]
    enddate = get_date(input)["enddate"]
    output = '<b> Vorlesungen: </b> \n \n'


    if tag == "VORLESUNGEN":
        
        #get all modules for the user
        my_modules = my_session.query(enrolement_table).join(Student).join(Module).filter(Student.telegram_id == user_id)
        modules= []
        #append the module id in list for lecture query
        for module in my_modules:
            id = module.modules_id
            name = my_session.query(Module).filter(Module.id == id).first().module_name

            modules.append(id)

        #get all lectures for user, module, date
        lectures = my_session.query(Lecture_infos).filter((Lecture_infos.module_id.in_(modules)) & (Lecture_infos.start_dt >= startdate) & (Lecture_infos.end_dt <= enddate)).order_by(Lecture_infos.start_dt.asc())

        if lectures.first() == None:
                return ["Keine Vorlesungen an diesem Termin!"]

        for lecture in lectures:
                module_name = my_session.query(Module).filter(Module.id == lecture.module_id).first().module_name
                start = str(lecture.start_dt)
                end = str(lecture.end_dt).split(' ')[1]
                weekday = weekdays.get(lecture.start_dt.weekday())
                room = lecture.room
                output += f'<b> {module_name}: </b> {weekday}: {start} - {end} (Raum: {room}) \n'
        
    else:
        #search if user has module
        module = my_session.query(enrolement_table).join(Student).join(Module).filter((Student.telegram_id == user_id) & (Module.module_name.like(f'%{tag}%'))).first()

        if module == None:
            return ['Sie haben dieses Modul nicht belegt!']
        else:
            id = module.modules_id
            name = my_session.query(Module).filter(Module.id == id).first().module_name

            dates = my_session.query(Lecture_infos).filter((Lecture_infos.module_id == id) & (Lecture_infos.start_dt >= startdate) & (Lecture_infos.end_dt <= enddate) )
            
            if dates.first() == None:
                return ["Keine Vorlesungen an diesem Termin!"]

            for date in dates:
                start = str(date.start_dt)
                end = str(date.end_dt).split(' ')[1]
                weekday = weekdays.get(date.start_dt.weekday())
                room = date.room
                output += f'<b> {name}: </b> {weekday}: {start} - {end} (Raum: {room}) \n'

            output += '\n'

    
    output = [output]


    return output



def get_output(tag, input, user_id):
    function = func_list.get(tag)
    download_tag = download_tags.get(tag)

    if function == get_news:
        return function()
    elif function == get_downloads:
        return function(download_tag)
    elif function == get_lecture_info:
        return function(tag, input, user_id)
    elif function == get_infos:
        return function(download_tag)



#define dictionaries for functions
func_list = {
    'AKTUELLES': get_news,
    'INFORMATIONEN_STUDIUM': get_downloads,
    'BEURLAUBUNG': get_downloads,
    'LEISTUNGSANNERKENNUNG': get_infos,
    'MODULBESCHREIBUNGEN': get_downloads,
    'PRÜFUNGSLEISTUNGEN': get_downloads,
    'STUDIENORDNUNG': get_downloads,
    'STUDIUM_GENERALE': get_infos,
    'UNBEDENKLICHKEIT': get_downloads,
    'EXMATRIKULIERUNG': get_downloads,
    'SUMMERSCHOOL': get_downloads,
    'PRAXISSEMESTER': get_infos,
    'BACHELORARBEIT': get_downloads,
    'AUSLANDSAMT': get_downloads,
    'VORLESUNGEN': get_lecture_info,
}

all_modules = my_session.query(Module)

for module in all_modules:
    name = module.module_name.replace('Wahlfach ', '')
    name = name.replace('Wahlfach: ', '')

    func_list[f'{name}'] =  get_lecture_info

download_tags = {
    'INFORMATIONEN_STUDIUM': 'Allgemeine Informationen zum Studium',
    'BEURLAUBUNG': 'Antrag auf Beurlaubung',
    'LEISTUNGSANNERKENNUNG': 'Anerkennungen',
    'MODULBESCHREIBUNGEN': 'Modul-/Lehrveranstaltungsbeschreibungen',
    'PRÜFUNGSLEISTUNGEN': 'Prüfungsleistungen',
    'STUDIENORDNUNG': 'Studien- und Prüfungsordnung',
    'STUDIUM_GENERALE': 'Studium Generale',
    'UNBEDENKLICHKEIT': 'Unbedenklichkeitserklärung',
    'EXMATRIKULIERUNG': 'Antrag auf Exmatrikulation',
    'SUMMERSCHOOL': 'Summer School',
    'PRAXISSEMESTER': 'Praxissemester',
    'BACHELORARBEIT': 'Bachelorarbeit',
    'AUSLANDSAMT': 'Akademisches Auslandsamt',
}

weekdays = {
    0: 'Montag',
    1: 'Dienstag',
    2: 'Mittwoch',
    3: 'Donnerstag',
    4: 'Freitag',
    5: 'Samstag'
}
