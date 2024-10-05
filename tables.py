import os
from dataclasses import dataclass
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, func, ForeignKey
from datetime import datetime
from sqlalchemy.orm import declarative_base, sessionmaker

DBUSER=os.getenv("DBUSER")
DBPASS=os.getenv("DBPASS")
DBIP=os.getenv("DBIP")
DB=os.getenv("DB")

engine = create_engine(f'mysql+pymysql://{DBUSER}:{DBPASS}@{DBIP}/{DB}')
Base = declarative_base()

@dataclass
class User(Base):
    __tablename__ = 'users'
    id:int = Column(Integer, primary_key=True)
    name:str = Column(String)

@dataclass
class Admin(Base):
    __tablename__ = 'admins'
    id: int = Column(Integer, primary_key=True)
    username: str = Column(String, unique=True, nullable=False)
    password: str = Column(String, nullable=False)
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

@dataclass
class Event(Base):
    __tablename__ = 'events'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String, nullable=False)
    description: str = Column(Text)
    startdate: datetime = Column(DateTime, nullable=False)
    starttime: str = Column(String, nullable=False)
    enddate: datetime = Column(DateTime, nullable=False)
    endtime: str = Column(String, nullable=False)
    venue: str = Column(String, nullable=False)
    eventtype: str = Column(String)
    minparticipants: int = Column(Integer)
    maxparticipants: int = Column(Integer)
    registrationfee: float = Column(String, nullable=False)
    rulebooklink: str = Column(String)
    # To handle heads as a list of objects containing headName and 
    # headPhoneNumber, and tags as a list of tags,
    # JSON serialization can be used.
    # Eg: 
    # tags_list = ["technology", "talk", "seminar"]
    # new_event.set_tags(tags_list)
    heads: str = Column(Text, nullable=False)  
    tags: str = Column(Text, nullable=False)   
    image: str = Column(String, nullable=True)  # Image URL, can be null
    participationType: str = Column(String, nullable=False)
    paymentType: str = Column(String, nullable=False)
    ruleBookType: str = Column(String, nullable=False)
    adminId: int = Column(Integer, ForeignKey('admins.id'), nullable=False)  # Foreign key to Admin table


Session = sessionmaker(bind=engine)

class DBConnectionManager:
    def __enter__(self):
        self.session = Session()
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()
        if exc_type or exc_value or traceback:
            self.session.rollback()  # Rollback in case of exception
            print(f"An error occurred: {exc_value}")
        return False
