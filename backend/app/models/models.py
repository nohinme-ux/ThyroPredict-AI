import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="researcher", nullable=False)
    account_status = Column(String(50), default="active", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    predictions = relationship("Prediction", back_populates="creator")

class ResearchParticipant(Base):
    __tablename__ = "research_participants"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    research_participant_code = Column(String(100), unique=True, index=True, nullable=False)
    display_name = Column(String(255), nullable=True) # Optional pseudonymized identifier
    age = Column(Float, nullable=True)
    sex = Column(String(10), nullable=True)
    consent_status = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    predictions = relationship("Prediction", back_populates="participant", cascade="all, delete-orphan")

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    participant_id = Column(String(36), ForeignKey("research_participants.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    model_name = Column(String(100), nullable=False) # "sts_clinical" or "uci_benchmark"
    model_version = Column(String(50), nullable=False)
    submitted_feature_values = Column(JSON, nullable=False)
    predicted_class = Column(String(100), nullable=False, index=True)
    class_probabilities = Column(JSON, nullable=True)
    explanation_rules = Column(JSON, nullable=True)
    feature_importances = Column(JSON, nullable=True)
    record_status = Column(String(50), default="active", nullable=False)
    prediction_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    participant = relationship("ResearchParticipant", back_populates="predictions")
    creator = relationship("User", back_populates="predictions")

class ModelVersionRecord(Base):
    __tablename__ = "model_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    model_id = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    artifact_identifier = Column(String(255), nullable=False)
    dataset_fingerprint = Column(String(100), nullable=False)
    accuracy = Column(Float, nullable=False)
    balanced_accuracy = Column(Float, nullable=True)
    macro_f1 = Column(Float, nullable=False)
    approval_status = Column(String(50), default="approved", nullable=False)
    limitations = Column(JSON, nullable=True)
    training_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
