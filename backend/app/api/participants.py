from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from backend.app.core.database import get_db
from backend.app.models.models import ResearchParticipant, Prediction, User
from backend.app.schemas.schemas import ParticipantCreate, ParticipantUpdate, ParticipantResponse
from backend.app.api.auth import get_current_user

router = APIRouter(prefix="/participants", tags=["Research Participants"])

@router.get("", response_model=List[ParticipantResponse])
def list_participants(
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(ResearchParticipant)
    if search:
        s = f"%{search}%"
        query = query.filter(
            (ResearchParticipant.research_participant_code.ilike(s)) |
            (ResearchParticipant.display_name.ilike(s))
        )
    participants = query.order_by(ResearchParticipant.created_at.desc()).offset(skip).limit(limit).all()

    # Annotate with prediction count
    result = []
    for p in participants:
        count = db.query(Prediction).filter(Prediction.participant_id == p.id).count()
        p_dict = ParticipantResponse.model_validate(p)
        p_dict.prediction_count = count
        result.append(p_dict)
    return result

@router.post("", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED)
def create_participant(
    data: ParticipantCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    existing = db.query(ResearchParticipant).filter(
        ResearchParticipant.research_participant_code == data.research_participant_code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Participant code already exists in registry")

    new_p = ResearchParticipant(
        research_participant_code=data.research_participant_code,
        display_name=data.display_name,
        age=data.age,
        sex=data.sex,
        consent_status=data.consent_status,
        notes=data.notes
    )
    db.add(new_p)
    db.commit()
    db.refresh(new_p)
    resp = ParticipantResponse.model_validate(new_p)
    resp.prediction_count = 0
    return resp

@router.get("/{id}", response_model=ParticipantResponse)
def get_participant(id: str, db: Session = Depends(get_db)):
    p = db.query(ResearchParticipant).filter(ResearchParticipant.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Participant not found")
    count = db.query(Prediction).filter(Prediction.participant_id == p.id).count()
    resp = ParticipantResponse.model_validate(p)
    resp.prediction_count = count
    return resp

@router.put("/{id}", response_model=ParticipantResponse)
def update_participant(
    id: str,
    update_data: ParticipantUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    p = db.query(ResearchParticipant).filter(ResearchParticipant.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Participant not found")

    if update_data.display_name is not None:
        p.display_name = update_data.display_name
    if update_data.age is not None:
        p.age = update_data.age
    if update_data.sex is not None:
        p.sex = update_data.sex
    if update_data.consent_status is not None:
        p.consent_status = update_data.consent_status
    if update_data.notes is not None:
        p.notes = update_data.notes

    p.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(p)
    count = db.query(Prediction).filter(Prediction.participant_id == p.id).count()
    resp = ParticipantResponse.model_validate(p)
    resp.prediction_count = count
    return resp

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_participant(
    id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    p = db.query(ResearchParticipant).filter(ResearchParticipant.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Participant not found")
    db.delete(p)
    db.commit()
    return None
