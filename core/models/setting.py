from sqlalchemy import Column, String

from core.database import Base


class Setting(Base):
    __tablename__ = "setting"

    key = Column(String, primary_key=True)
    value = Column(String)
