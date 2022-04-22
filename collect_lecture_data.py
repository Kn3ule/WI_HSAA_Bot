from sys import modules

from sqlalchemy import desc
from icalendar import Calendar
from datetime import datetime, timedelta, timezone
from numpy import blackman
import requests
from postgres import my_session, Student, Module



""" for component in cal.walk():
    if component.name == "VEVENT":
        summary = component.get('summary')
        print(summary)
        description = component.get('description')
        print(description)
        location = component.get('location')
        startdt = component.get('dtstart').dt
        enddt = component.get('dtend').dt
        exdate = component.get('exdate') """

#funktion zum auslesen der Modulinfos aus den ical Dateien
def get_module_from_ical(cal):
    modules = []
    for component in cal.walk():
        if component.name == 'VEVENT':
            description = component.get('description')
            description = description.split('\\n')
            
            for x in description:
                parts = x.split('\n')

                if len(parts) == 6:
                    del parts[3]

                name = parts[0].split('(')[0][:-1]
                try:
                    number = parts[0].split('(')[1].replace(')', '')
                except:
                    number= ''

                lecturer = parts[1]
                semester = parts[2]

                if len(parts) > 4:
                    canvas = parts[3].split(' ')[1]
                else:
                    canvas = ''

                entry = {
                    "name": name,
                    "number": number,
                    "lecturer": lecturer,
                    "semester": semester,
                    "canvas": canvas,
                }
                
                if entry not in modules:
                    modules.append(entry)
    
    return modules

#erstellen der Objekte der Module
def create_module(name, number, lecturer, semester, canvas):
    module = Module(module_name= name, module_number = number, lecturer= lecturer, semester=semester, canvas=canvas)
    
    my_session.add(module)
    my_session.commit()


def main():
    calWI2 = Calendar.from_ical(open('splan_SoSe22_WI_S2.ics','rb').read())
    calWI4 = Calendar.from_ical(open('splan_SoSe22_WI_S4.ics','rb').read())
    calWI6 = Calendar.from_ical(open('splan_SoSe22_WI_S6.ics','rb').read())

    calWI = [calWI2, calWI4, calWI6]
    
    #get the module infos from the ical and create Objects in the Database
    for cal in calWI:
        modules = get_module_from_ical(cal)
        for module in modules:
            create_module(module["name"], module["number"], module["lecturer"], module["semester"], module["canvas"])
    

if __name__ == '__main__':
    main()