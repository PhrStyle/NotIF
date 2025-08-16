from sqlalchemy.orm import relationship
from sqlalchemy import Integer, String, Column, Boolean, Text

from .base import Base

class Screens(Base):
    __tablename__ = 'screens'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    temRodape = Column(Boolean, default=True, nullable=False)
    footer_text = Column(Text, nullable=True)  # Texto do rodapé
    screen_files = relationship("ScreenFiles", backref="screen", cascade="all, delete")
