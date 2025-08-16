from models.screens import Screens
from db_init import SessionLocal

def buscar_telas(nome=None):
    session = SessionLocal()
    query = session.query(Screens)
    if nome:
        query = query.filter(Screens.nome.ilike(f"%{nome}%"))
    telas = query.all()
    session.close()
    return telas
