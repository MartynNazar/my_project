from sqlalchemy import Column, Integer, String

from services.database import Base


class Song(Base):
    __tablename__ = 'songs'
    id = Column(Integer, primary_key=True)
    year = Column(Integer)
    name = Column(String)
    author = Column(String)
    audio = Column(String)
    genre = Column(String)

    def __str__(self):
        return f"{self.year=} {self.name=} {self.author=} {self.audio=} {self.genre=}"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
