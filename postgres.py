from datetime import datetime
from dotenv import load_dotenv
import os
from sqlalchemy import Column, ForeignKey, Integer, create_engine, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import Integer, String,BigInteger,DateTime
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine(os.getenv("POSTGRES_URL"))
base = declarative_base()
conn = engine.connect()
Session = sessionmaker()
my_session = Session(bind=engine)


enrolement_table = Table('enrolements', base.metadata,
    Column('modules_id', ForeignKey('modules.id'), primary_key=True),
    Column('students_id', ForeignKey('students.telegram_id'), primary_key=True)
)


class Student(base):
    __tablename__='students'

    telegram_id = Column(BigInteger, primary_key=True)
    first_name = Column(String(10), nullable=False)
    last_name = Column(String(20),nullable=False)
    modules = relationship(
        "Module",
        secondary= enrolement_table,
        back_populates="students"
    )

    def __init__(self, telegram_id, first_name, last_name):
        self.telegram_id = telegram_id
        self.first_name = first_name
        self.last_name = last_name

class Module(base):
    __tablename__ = 'modules'

    id = Column(Integer, primary_key=True, autoincrement=True)
    module_name = Column(String, nullable = False)
    module_number = Column(String, nullable = False)
    lecturer = Column(String, nullable = False)
    semester = Column(String, nullable = False)
    canvas = Column(String, nullable = False)
    students = relationship(
        "Student",
        secondary= enrolement_table,
        back_populates="modules"
    )

    def __init__(self, module_name, module_number, lecturer, semester, canvas):
        self.module_name = module_name
        self.module_number = module_number
        self.lecturer = lecturer
        self.semester = semester
        self.canvas = canvas

class Lecture_infos(base):
    __tablename__ = 'lecture_infos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    modul_id = Column(Integer, ForeignKey('modules.id'))
    datetime = Column(DateTime)
    room = Column(String)

    def __init__(self, id, modul_id, day, time, room):
        self.id = id
        self.modul_id = modul_id
        self.day = day
        self.time = time
        self.room = room


def create_tables():
    base.metadata.create_all(conn)

if __name__ == "__main__":
    create_tables()