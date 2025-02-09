from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas

def get_document(db: Session, document_id: int) -> Optional[models.Document]:
    """Get a single document by ID"""
    return db.query(models.Document).filter(models.Document.id == document_id).first()

def get_documents(
    db: Session, 
    skip: int = 0, 
    limit: int = 10,
    agent_id: Optional[int] = None
) -> List[models.Document]:
    """Get all documents with optional filtering by agent_id"""
    query = db.query(models.Document)
    if agent_id is not None:
        query = query.filter(models.Document.agent_id == agent_id)
    return query.offset(skip).limit(limit).all()

def create_document(db: Session, document: schemas.DocumentCreate) -> models.Document:
    """Create a new document"""
    db_document = models.Document(
        type=document.type,
        source=document.source,
        agent_id=document.agent_id
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def delete_document(db: Session, document_id: int) -> Optional[models.Document]:
    """Delete a document"""
    db_document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if db_document is None:
        return None
    
    db.delete(db_document)
    db.commit()
    return db_document

def delete_agent_documents(db: Session, agent_id: int) -> int:
    """Delete all documents for an agent"""
    result = db.query(models.Document).filter(models.Document.agent_id == agent_id).delete()
    db.commit()
    return result