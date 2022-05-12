from datetime import date, timedelta
from nlp import preprocess
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import feedparser
import ssl
from postgres import *
from telegram import Update

hsaa = "www.hs-aalen.de"
basic_url = "https://www.hs-aalen.de/de/courses/39"
downloads = f"{basic_url}/downloads"
news = f"{basic_url}/news"


def get_downloads(input):
    driver = webdriver.Chrome(ChromeDriverManager().install())

    driver.get(f"{basic_url}/downloads")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.close()
    #panel = soup.find('div',class_='panel', text='Allgemeine Informationen zum Studium')
    panel = soup.find_all('div',class_='panel')

    try:
        for p in panel:
            if p.find('div', text=input) != None:
                head = p.find('div', text=input)
                data = p.find_all('div', class_='paragraph')


        heading = f'<b>  {str(head.get_text())} </b> \n'
        output = heading
        for d in data:
            text = str(d.get_text())
            link = hsaa + str(d.find('a').get('href'))

            output = f'{output} \n <strong> {text} </strong> \n <a href="{link}"> {text} </a> \n'
    except Exception:
        output = "Ich konnte zu diesem Thema nichts finden"

    return output

def get_news():
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context
    feed = feedparser.parse(f'{basic_url}/infos.rss')

    #check if 
    if len(feed.entries) == 0:
        return 'Keine Neuigkeiten im Studiengang Wirtschaftsinformatik'


    output = f'<b>  Neues im Studiengang Wirtschaftsinformatik: </b> \n\n'
    for e in feed.entries:
        title = f'{e.title}\n'

        output = f'{output} {title}\n'

    output = f'{output} mehr sehen: {basic_url}/news'
    
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
        for lecture in lectures:
                module_name = my_session.query(Module).filter(Module.id == lecture.module_id).first().module_name
                start = str(lecture.start_dt)
                end = str(lecture.end_dt).split(' ')[1]
                room = lecture.room
                output += f'<b> {module_name}: </b> {start} - {end} (Raum: {room}) \n'
        
    else:
        #search if user has module
        module = my_session.query(enrolement_table).join(Student).join(Module).filter((Student.telegram_id == user_id) & (Module.module_name.like(f'%{tag}%'))).first()

        if module == None:
            return 'Sie haben dieses Modul nicht belegt!'
        else:
            id = module.modules_id
            name = my_session.query(Module).filter(Module.id == id).first().module_name

            output += f'{name}: \n'


            dates = my_session.query(Lecture_infos).filter((Lecture_infos.module_id == id) & (Lecture_infos.start_dt >= startdate) & (Lecture_infos.end_dt <= enddate) )
            if dates == None:
                return "Keine Vorlesungen an diesem Termin!"
            for date in dates:
                start = str(date.start_dt)
                end = str(date.end_dt).split(' ')[1]
                room = date.room
                output += f'{start} - {end} (Raum: {room}) \n'

            output += '\n'



    return output

func_list = {
    'AKTUELLES': get_news,
    'INFORMATIONEN_STUDIUM': get_downloads,
    'BEURLAUBUNG': get_downloads,
    'LEISTUNGSANNERKENNUNG': get_downloads,
    'MODULBESCHREIBUNGEN': get_downloads,
    'PRÜFUNGSLEISTUNGEN': get_downloads,
    'STUDIENORDNUNG': get_downloads,
    'STUDIUM_GENERALE': get_downloads,
    'UNBEDENKLICHKEIT': get_downloads,
    'EXMATRIKULIERUNG': get_downloads,
    'SUMMERSCHOOL': get_downloads,
    'PRAXISSEMESTER': get_downloads,
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
    'LEISTUNGSANNERKENNUNG': 'Antrag auf Leistungsanerkennung',
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

def get_output(tag, input, user_id):
    function = func_list.get(tag)
    download_tag = download_tags.get(tag)

    if function == get_news:
        return function()
    elif function == get_downloads:
        return function(download_tag)
    elif function == get_lecture_info:
        return function(tag, input, user_id)

if __name__ == '__main__':
    print(get_lecture_info("VORLESUNGEN", "Was habe ich diese Woche für eine Vorlesung?"))