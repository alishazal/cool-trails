from sqlalchemy import Column, Integer, String, Float, Text
from database import Base

class Trail(Base):
    __tablename__ = "trails"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    location = Column(String, index=True)
    description = Column(String, index=True)
    polygon = Column(Text)
