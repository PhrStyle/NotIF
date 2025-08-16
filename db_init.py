import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models.base import Base

import models

SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', 'notif.sqlite')
DATABASE_URL = f"sqlite:///{SQLITE_DB_PATH}"

# Criação do engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = scoped_session(sessionmaker(bind=engine))

def init_db():
    try:
        # Criação das tabelas
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(e)