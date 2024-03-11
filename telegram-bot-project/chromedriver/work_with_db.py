from data_db import db_session
from data_db.manga import Manga


db_session.global_init("db/catalog_manga.sqlite")