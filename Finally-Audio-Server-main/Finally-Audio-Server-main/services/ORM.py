from services.database import engine, Base, session_factory
from services.models import Song, User


class ORM:
    @staticmethod
    def create_tables():
        Base.metadata.create_all(engine)

    @staticmethod
    def drop_tables():
        Base.metadata.drop_all(engine)
        return []

    @staticmethod
    def add_record(record):
        with session_factory() as session:
            session.add(record)
            session.commit()

    @staticmethod
    def delete_record(song_id):
        with session_factory() as session:
            song = session.query(Song).get(song_id)
            session.delete(song)
            session.commit()
    @staticmethod
    def get_all_users():
        with session_factory() as session:
            users = session.query(Song).all()
            return users


    @staticmethod
    def change_record(song_id, record, year, name, author, genre):
        with session_factory() as session:
            #song = session.query(Song).filter(Song.id == song_id).first()
            song = session.query(Song).get(song_id)
            song.name = name
            song.year = year
            song.author = author
            song.genre = genre
            session.commit()


    @staticmethod
    def get_song_by_id(song_id):
        with session_factory() as session:
            song = session.query(Song).get(song_id)
            return song

    @staticmethod
    def get_correct_user(user_name, user_password):
        with session_factory() as session:
            user = session.query(User).filter(User.username == user_name, User.password == user_password).first()
            return user.username

    @staticmethod
    def add_user(user):
        with session_factory() as session:
            session.add(user)
            session.commit()
