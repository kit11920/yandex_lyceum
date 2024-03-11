import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Manga(SqlAlchemyBase):
    __tablename__ = 'manga'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    url = sqlalchemy.Column(sqlalchemy.String, nullable=True)