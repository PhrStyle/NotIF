from db_init import SessionLocal
from models import Files, ScreenFiles


def buscar_files_por_screen(screen):
    """
    Recebe o session do SQLAlchemy e um objeto Screen (ou screen_id),
    retorna lista de objetos File relacionados.
    """
    screen_id = screen.id if hasattr(screen, 'id') else screen  # aceita objeto ou id

    session = SessionLocal()
    # Query para buscar os files relacionados via tabela associativa
    files = (
        session.query(Files)
        .join(ScreenFiles, Files.id == ScreenFiles.file_id)
        .filter(ScreenFiles.screen_id == screen_id)
        .all()
    )
    return files