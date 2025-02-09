from sqlalchemy import Column, Integer, String

from ..database import Base, engine

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    index_name = Column(String, index=True, unique=True)

Base.metadata.create_all(bind=engine)