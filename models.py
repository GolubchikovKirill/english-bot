from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String)
    words = relationship("UserWord", back_populates="user")

class Word(Base):
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True)
    english = Column(String)
    russian = Column(String)
    created_by = Column(Integer, ForeignKey("users.id"))

class UserWord(Base):
    __tablename__ = 'user_words'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    word_id = Column(Integer, ForeignKey("words.id"))
    learned = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)
    user = relationship("User", back_populates="words")
    word = relationship("Word")