from sqlalchemy import UUID, Column, ForeignKey, Integer, String

from ..database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, index=True)  # External document ID
    type = Column(String)
    source = Column(String)

    # Foreign key to link to exactly one agent
    agent_id = Column(UUID(as_uuid=True), ForeignKey(
        "agents.id", ondelete="CASCADE"), nullable=False)
