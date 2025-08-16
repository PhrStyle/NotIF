from sqlalchemy import Column, Integer, String, Boolean
from .base import Base

class Files(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    file_name = Column(String(255), nullable=False, unique=True)  # Nome único para evitar duplicatas
    file_path = Column(String(500), nullable=False)  # Caminho completo do arquivo
    is_video = Column(Boolean, default=False, nullable=False)
    original_name = Column(String(255), nullable=True)  # Nome original do arquivo antes de ser renomeado
