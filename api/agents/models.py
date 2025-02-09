import uuid
from sqlalchemy.orm import relationship
from sqlalchemy import UUID, Column, Integer, String

from ..database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    description = Column(String)
    index_name = Column(String, index=True, unique=True)

    # One-to-many relationship: one agent has many documents
    documents = relationship("Document",
                             backref="agent",
                             cascade="all, delete-orphan",
                             uselist=True)
