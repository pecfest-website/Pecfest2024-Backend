import os
from dataclasses import dataclass
from sqlalchemy import create_engine, Column, Integer, String, DateTime
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
    id:int = Column(Integer, primary_key=True)
    name:str = Column(String)

@dataclass
class Event(Base):
    __tablename__ = 'events'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)
    date: datetime = Column(DateTime)
    time: str = Column(String) # image url
    image: str = Column(String)
    heads: str = Column(String)  
    tags: str = Column(String)  
    description: str = Column(String)


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
