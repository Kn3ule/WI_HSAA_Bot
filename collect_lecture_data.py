from sqlalchemy import desc
from icalendar import Calendar
from postgres import my_session, Student, Module, Lecture_infos


#function to read the modules
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

#function to read the lecture dates
def get_lecture_dates_from_ical(cal):
    lecture_data = []

    for component in cal.walk():
        if component.name == "VEVENT":
            name = component.get('description').replace('\\n', '').split('\n')[0].split('(')[0][:-1]
            startdt = component.get('dtstart').dt
            enddt = component.get('dtend').dt
            room = component.get('location').split(',')[0]

            if room == "Canvas" or room == "--":
                room = "online"

            entry = {
                    "name": name,
                    "startdt": startdt,
                    "enddt": enddt,
                    "room": room
                }
            lecture_data.append(entry)
    
    return lecture_data


#erstellen der Objekte der Module
def create_module(name, number, lecturer, semester, canvas):
    module = Module(module_name= name, module_number = number, lecturer= lecturer, semester=semester, canvas=canvas)
    
    my_session.add(module)
    my_session.commit()

def create_lecture_date(name, startdt, enddt, room):
    module = my_session.query(Module).filter(Module.module_name == name).first()
    module_id = module.id
    
    lecture_date = Lecture_infos(module_id = module_id, start_dt = startdt, end_dt = enddt, room = room)
    my_session.add(lecture_date)
    my_session.commit()


def main():
    calWI2 = Calendar.from_ical(open('splan_SoSe22_WI_S2.ics','rb').read())
    calWI4 = Calendar.from_ical(open('splan_SoSe22_WI_S4.ics','rb').read())
    calWI6 = Calendar.from_ical(open('splan_SoSe22_WI_S6.ics','rb').read())

    #calWI = [calWI2, calWI4, calWI6]
    calWI = [Calendar.from_ical(open('splan_evaluation.ics','rb').read())]

    #get the module infos from the ical and create Objects in the Database
    for cal in calWI:
        modules = get_module_from_ical(cal)
        for module in modules:
            create_module(module["name"], module["number"], module["lecturer"], module["semester"], module["canvas"])

    for cal in calWI:
        lecture_data = get_lecture_dates_from_ical(cal)
        for date in lecture_data:
            create_lecture_date(date['name'], date['startdt'], date['enddt'], date['room'])
    

if __name__ == '__main__':
    main()