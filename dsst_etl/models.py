from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Works(Base):
    __tablename__ = "works"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())
    initial_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    primary_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    provenance_id = Column(Integer, ForeignKey("provenance.id"))

    # Relationships
    # initial_document = relationship("Documents", back_populates="works_initial", foreign_keys=[initial_document_id])
    # primary_document = relationship("Documents", back_populates="works_primary", foreign_keys=[primary_document_id])
    # provenance = relationship("Provenance")


class Documents(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    hash_data = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=func.now())
    s3uri = Column(Text, nullable=False)
    provenance_id = Column(Integer, ForeignKey("provenance.id"))
    work_id = Column(Integer, ForeignKey("works.id"))

    # Relationships
    # provenance = relationship("Provenance")


class Provenance(Base):
    __tablename__ = "provenance"

    id = Column(Integer, primary_key=True)
    pipeline_name = Column(String(255))
    version = Column(String(50))
    compute = Column(Text)
    personnel = Column(Text)
    comment = Column(Text)
