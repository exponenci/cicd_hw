from os import getenv
from sys import exit as exit_f

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

from bot.keyboards.keyboards_dp import register_common_keyboard

Base = declarative_base()


class File(Base):
    """
    Class describing object `File`
    """
    __tablename__ = 'file'

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(String, unique=True)
    file_type = Column(String)
    holder_id = Column(String)
    code = Column(String)
    password = Column(String, default='-')
    views_count = Column(Integer, default=0)

    def __init__(self, init_dict: dict):
        for prop_name, value in init_dict.items():
            setattr(self, prop_name, value)

    def __repr__(self):
        return "<File(holder='%s', file_id='%s', file_type='%s')>" % \
               (self.holder_id, self.file_id, self.file_type)

    @property
    def caption(self):
        return f"That is your file: <file_id: {self.file_id[:9]}>\n\n" \
               f"Views: {self.views_count}\n\n"


class User(Base):
    """
    Class describing object `User`
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, unique=True)

    def __init__(self, user_id: int):
        self.user_id = user_id

    def __repr__(self):
        return "<User(user_id='%s')>" % self.user_id


class Database:
    """
    Class for working with SQLAlchemy sessions
    """

    def __init__(self, db_name):
        engine = create_engine(db_name)
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)
        session.configure(bind=engine)
        self.session = session()

    def register_user(self, user_id: int) -> bool:
        with self.session:
            if self.session.query(User).filter(User.user_id == user_id).count() == 0:
                self.session.add(User(user_id))
                self.session.commit()
                return True
            return False

    def add_new_file(self, file_data: dict):
        with self.session:
            self.session.add(File(file_data))
            self.session.commit()

    def get_users_files(self, user_id: int):
        with self.session:
            return self.session.query(File).filter(File.holder_id == user_id).all()

    def get_file(self, file_code: str):
        with self.session:
            return self.session.query(File).filter(File.code == file_code).first()

    def increment_file_views(self, file_code: str):
        with self.session:
            file_instance = self.session.query(File).filter(
                    File.code == file_code).first()
            if file_instance:
                file_instance.views_count += 1
                self.session.commit()

    def delete_file(self, file_id: str):
        with self.session:
            query = self.session.query(File).filter(File.file_id == file_id)
            if query.count():
                query.delete()
                self.session.commit()


class GlobalValues(dict):
    def __init__(self):
        super().__init__()


keyboards_dp = register_common_keyboard()
database_name = getenv("DATABASE_NAME")
if not database_name:
    exit_f("Error: no database name provided")
db = Database(database_name)
file_type_to_method = {
    "document": "answer_document",
    "photo":    "answer_photo",
    "video":    "answer_video",
    "voice":    "answer_voice",
    "audio":    "answer_audio"
}
global_values_container = GlobalValues()
