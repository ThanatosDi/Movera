from sqlalchemy import Column, String

from backend.database import Base


class Setting(Base):
    __tablename__ = "setting"

    key = Column(String, primary_key=True)
    value = Column(String)
