from cgitb import text
from curses import panel
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import feedparser
import ssl

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

        #text = e.summary
        #date = e.published

        output = f'{output} {title}\n'

    output = f'{output} mehr sehen: {basic_url}/news'
    
    return output