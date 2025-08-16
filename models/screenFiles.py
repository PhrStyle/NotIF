from sqlalchemy import Column, Integer, ForeignKey, Boolean, String, Enum
from sqlalchemy.orm import relationship
import enum

from .base import Base

class SideEnum(enum.Enum):
    LEFT = "left"
    RIGHT = "right"

class MediaTypeEnum(enum.Enum):
    FILE = "file"
    INSTAGRAM = "instagram"

class ScreenFiles(Base):
    __tablename__ = 'screenfiles'

    id = Column(Integer, primary_key=True)
    screen_id = Column(Integer, ForeignKey('screens.id'))
    file_id = Column(Integer, ForeignKey('files.id'), nullable=True)
    side = Column(Enum(SideEnum), nullable=False)
    has_audio = Column(Boolean, default=True, nullable=False)
    media_type = Column(Enum(MediaTypeEnum), default=MediaTypeEnum.FILE, nullable=False)
    instagram_profile = Column(String(255), nullable=True)  # Para integração com Instagram
    order_position = Column(Integer, default=0, nullable=False)  # Para ordenação dos arquivos
    
    files = relationship("Files", backref="screenfiles")
    screens = relationship("Screens", backref="screenfiles")
