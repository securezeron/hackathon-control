from sqlalchemy import Column, Integer, String, DateTime, Sequence
from .session import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_login = Column(Integer)
    jwt_token = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True, index=True)
    name = Column(String)
    date_time = Column(DateTime, default=datetime.utcnow)


class Levels(Base):
    __tablename__ = "levels"

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True, index=True)
    name = Column(String)
    score = Column(Integer)
    flag = Column(String)
    priority = Column(Integer)
    endpoint = Column(String)


class Flags(Base):
    __tablename__ = "flags"

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True, index=True)
    user_id = Column(Integer)
    level_id = Column(Integer)
    is_submitted = Column(Integer)

class ScoreBoard(Base):

    __tablename__ = "score_board"

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True, index=True)
    user_id = Column(Integer)
    final_score = Column(Integer)

    
