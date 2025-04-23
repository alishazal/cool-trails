from sqlalchemy import Column, Integer, BigInteger, String, Float, Text
from database import Base

class Trail(Base):
    __tablename__ = "trails"

    id = Column(Integer, primary_key=True, index=True)
    osm_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String, index=True)
    location = Column(String, index=True)
    description = Column(String, index=True)
    polygon = Column(Text)
    center_lat = Column(Float)
    center_lng = Column(Float)
