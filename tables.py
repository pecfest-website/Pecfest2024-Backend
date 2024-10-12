import os
from dataclasses import dataclass
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, func, ForeignKey, Date, Time, Float, Boolean, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Mapped, backref
from typing import List
import datetime
from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import Enum as SqlEnum
from util.loggerSetup import logger

DBUSER=os.getenv("DBUSER")
DBPASS=os.getenv("DBPASS")
DBIP=os.getenv("DBIP")
DB=os.getenv("DB")

engine = create_engine(f'mysql+pymysql://{DBUSER}:{DBPASS}@{DBIP}/{DB}')
Base = declarative_base()

@dataclass
class User(Base):
    __tablename__ = 'users'
    id:int = Column(Integer, primary_key=True, autoincrement=True)
    name:str = Column(String, nullable=False)
    college:str = Column(String, nullable=False)
    sid:str = Column(String)
    email:str = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    contact:str = Column(String(10), nullable=False, unique=True)
    uuid:str = Column(String, nullable=False, unique=True)
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    teamMem = relationship("TeamMember", back_populates='user')
    
    def to_dict(self):
        return {
            "userId": self.id,
            "name": self.name,
            "email": self.email,
            "uuid": self.uuid
        }

@dataclass
class Admin(Base):
    __tablename__ = 'admins'
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    username: str = Column(String, unique=True, nullable=False)
    password: str = Column(String, nullable=False)
    domain: str = Column(String, nullable=False)
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "domain": self.domain
        }

class EventTypeEnum(Enum):
    CULTURAL = "Cultural"
    TECHNICAL = "Technical"
    WORKSHOP = "Workshop"
    MEGASHOW = "Megashow"

class ParticipationTypeEnum(Enum):
    SINGLE = 'Single'
    TEAM = 'Team'

class PaymentTypeEnum(Enum):
    FREE = "Free"
    PAID = 'Paid'

@dataclass
class Tag(Base):
    __tablename__ = 'tags'
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String, nullable=False)

@dataclass
class Head(Base):
    __tablename__ = 'heads'
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    eventId: int = Column(Integer, ForeignKey('events.id'), nullable=False)
    name: str = Column(String, nullable=False)
    phoneNumber: str = Column(String, nullable=False)
    event = relationship("Event", back_populates="heads")

@dataclass
class Participant(Base):
    __tablename__ = "participants"
    id: int = Column(Integer, primary_key=True, autoincrement=True)

    #It will contain userId in case of participationType = Single else it will contain team id.
    participantId: str = Column(String, nullable=False)
    eventId: int = Column(Integer, ForeignKey('events.id'), nullable=False)
    requireAccomodations: bool = Column(Boolean, nullable=False, default=False)
    paymentId: str = Column(String)
    paymentProof: str = Column(String)
    billingAddress: str = Column(String)
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    event = relationship("Event", back_populates="participants")

@dataclass
class Event(Base):
    __tablename__ = 'events'
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    adminId: int = Column(Integer, ForeignKey("admins.id"), nullable=False)
    name: str = Column(String, nullable=False)
    description: str = Column(String, nullable=False)
    startDate: datetime = Column(Date, nullable=False)
    startTime: datetime = Column(Time, nullable=False)
    endDate: datetime = Column(Date, nullable=False)
    endTime: datetime = Column(Time, nullable=False)
    venue: str = Column(String, nullable=False)
    eventType: EventTypeEnum = Column(SqlEnum(EventTypeEnum), nullable=False)
    participationType: ParticipationTypeEnum = Column(SqlEnum(ParticipationTypeEnum), nullable=False)
    minParticipants: int = Column(Integer)
    maxParticipants: int = Column(Integer)
    paymentType: PaymentTypeEnum = Column(SqlEnum(PaymentTypeEnum), nullable=False)
    registrationFee: float = Column(Float)
    haveRuleBook: bool = Column(Boolean, nullable=False)
    ruleBookLink: str = Column(String)
    provideAccommodation: bool = Column(Boolean, default=False, nullable=False)
    tags: list = Column(JSON)
    image: str = Column(String, nullable=True)
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    heads: Mapped[List[Head]] = relationship("Head", back_populates="event", cascade="all, delete-orphan")
    participants: Mapped[List[Participant]] = relationship("Participant", back_populates="event")

class MemberTypeEnum(Enum):
    INVITED = "invited"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

@dataclass
class TeamMember(Base):
    __tablename__ = "teamMembers"
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    userId: str = Column(String, ForeignKey("users.uuid"), nullable=False)
    memberType: MemberTypeEnum = Column(SqlEnum(MemberTypeEnum), nullable=False)
    teamId: int = Column(Integer, ForeignKey("teams.id"), nullable = False)
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    user:Mapped[List[User]] = relationship("User", back_populates="teamMem")
    team = relationship("Team", back_populates="members")

@dataclass
class Team(Base):
    __tablename__ = "teams"
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    teamName: str = Column(String, nullable=False)
    teamSize: int = Column(Integer, nullable=False)
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    members: Mapped[List[TeamMember]] = relationship("TeamMember", back_populates="team")

@dataclass
class Sponser(Base):
    __tablename__ = "sponsers"
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    link : str = Column(String, nullable = False)
    typeId: int = Column(Integer, ForeignKey('sponserTypes.id') ,nullable = False)
    isDeleted : bool = Column(Boolean, default=False, nullable=False)
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    sponserType = relationship("SponserType", back_populates="sponsers")

@dataclass
class SponserType(Base):
    __tablename__ = "sponserTypes"
   
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String, nullable = False)
    priorty: int = Column(Integer, nullable = False, default=1)
    isDeleted: bool = Column(Boolean, nullable=False, default=False)
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    sponsers: Mapped[List[Sponser]] = relationship("Sponser", back_populates="sponserType")

Session = sessionmaker(bind=engine)

class DBConnectionManager:
    def __enter__(self):
        self.session = Session()
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()
        if exc_type or exc_value or traceback:
            self.session.rollback()
            logger.error(f"An error occurred: {exc_value}")
        return False
