import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models.base import Base

import models
# Importar explicitamente o modelo User para garantir que seja registrado
from models.user import User

SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', 'notif.sqlite')
DATABASE_URL = f"sqlite:///{SQLITE_DB_PATH}"

# Criação do engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = scoped_session(sessionmaker(bind=engine))

def init_db():
    try:
        # Criação das tabelas
        Base.metadata.create_all(bind=engine)

        # Criar usuário padrão se não existir
        session = SessionLocal()

        default_username = os.getenv('DEFAULT_USERNAME')
        default_password = os.getenv('DEFAULT_PASSWORD')

        # Verificar se o usuário já existe
        existing_user = session.query(User).filter_by(username=default_username).first()
        if not existing_user:
            admin_user = User(username=default_username)
            admin_user.set_password(default_password)
            session.add(admin_user)
            session.commit()
            print(f"Usuário padrão '{default_username}' criado com sucesso!")
        else:
            print(f"Usuário '{default_username}' já existe.")

        session.close()

    except Exception as e:
        print(f"Erro na inicialização do banco: {e}")
        session.rollback() if 'session' in locals() else None
