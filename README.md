# WI_HSAA_Bot
In diesem Repository befindet sich der Source Code zu meiner Bachelorarbeit im Studiengang Wirtschaftsinformatik an der Hochschule Aalen.
Der Titel dieser Abschlussarbeit lautet: "Konzeption und Entwicklung eines Chatbots zur Informationsbeschaffung für Studierende des Studiengangs Wirtschaftsinformatik an der Hochschule Aalen".

## Benutzte Technologien:
- Python
- PostgreSQL
- Data Preprocessing mit NLTK & Pandas
- ML (Classification) mit Scikitlearn
- Kommunikation mit Telegram über die Python-Telegram-Bot Biliothek

## Installation:

### 1. öffne das Projekt in einem Texteditor (z.B. VS-Code)

### 2. Aufsetzen einer Postgres-Datenbank

- postgreSQL und pgAdmin installieren <br>

### 3. Telegram Bot über den BotFather erstellen

- Telegram öffnen und einen neuen Bot über den BotFather initieren <br>
- Gegebenen Token notieren

### 4. Erstellen Sie eine .env Datei im Projekt Ordner

- hinzufügen einer lokalen Variable für den Telegram Token<br>
  - TELEGRAM_TOKEN="{token}"<br>
- hinzufügen einer lokalen Variable für den Postgres Zugang<br>
  - POSTGRES_URL="postgresql://postgres:{Passwort}@localhost:{Port}/{Name der Datenbank}"

### 5. Installieren der benötigten Bibliotheken:

- Python-Telegram-Bot: pip install python-telegram-bot --upgrade<br>
- Pandas: pip install pandas<br>
- spacy: pip install -U pip setuptools wheel<br>
        pip install -U spacy<br>
        python -m spacy download de_core_news_sm<br>
- Scikit-learn: pip install -U scikit-learn<br>
- SQLAlchemy: pip install SQLAlchemy<br>
- Beautiful Soup: pip install beautifulsoup4<br>
- feedparser: pip install feedparser<br>
- requests: pip install requests<br>
- ICalendar: pip install icalendar<br>

### 6. Ausführen der Datein zur Vorbereitung

- Um Datenbank zu initieren postgres.py ausführen<br>
- Um Datenbank mit Infos zu Modulen zu füllen collect_lecture_data.py ausführen

### 7. Bot Starten
- Der bot kann über das python file tg_connection.py ausgeführt werden.


