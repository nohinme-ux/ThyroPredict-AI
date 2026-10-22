from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.app.core.database import get_db
from backend.app.models.models import Prediction, ResearchParticipant, User
from backend.app.schemas.schemas import PredictionRequest, PredictionResponse, OverviewStats
from backend.app.services.ml_service import ml_service
from backend.app.api.auth import get_current_user

router = APIRouter(prefix="", tags=["Predictions & Research Records"])

@router.post("/predictions", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
def create_prediction(
    req: PredictionRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    participant = db.query(ResearchParticipant).filter(ResearchParticipant.id == req.participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    if req.model_type == "sts_clinical":
        if not req.sts_features:
            raise HTTPException(status_code=422, detail="Missing required STS Clinical features")
        feature_data = req.sts_features.model_dump()
        try:
            ml_result = ml_service.predict_sts(feature_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")
    elif req.model_type == "uci_benchmark":
        if not req.uci_features:
            raise HTTPException(status_code=422, detail="Missing required UCI Benchmark features")
        feature_data = req.uci_features.model_dump()
        try:
            ml_result = ml_service.predict_uci(feature_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported model type: {req.model_type}")

    prediction_record = Prediction(
        participant_id=participant.id,
        created_by_user_id=current_user.id if current_user else None,
        model_name=ml_result["model_name"],
        model_version=ml_result["model_version"],
        submitted_feature_values=feature_data,
        predicted_class=ml_result["predicted_class"],
        class_probabilities=ml_result["class_probabilities"],
        explanation_rules=ml_result["explanation_rules"],
        feature_importances=ml_result["feature_importances"]
    )
    db.add(prediction_record)
    db.commit()
    db.refresh(prediction_record)

    return {
        "id": prediction_record.id,
        "participant_id": participant.id,
        "participant_code": participant.research_participant_code,
        "display_name": participant.display_name,
        "model_name": prediction_record.model_name,
        "model_version": prediction_record.model_version,
        "predicted_class": prediction_record.predicted_class,
        "class_probabilities": prediction_record.class_probabilities,
        "explanation_rules": prediction_record.explanation_rules,
        "feature_importances": prediction_record.feature_importances,
        "submitted_feature_values": prediction_record.submitted_feature_values,
        "prediction_timestamp": prediction_record.prediction_timestamp,
        "record_status": prediction_record.record_status
    }

@router.get("/predictions", response_model=List[PredictionResponse])
def list_predictions(
    participant_id: Optional[str] = None,
    model_name: Optional[str] = None,
    predicted_class: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(Prediction).join(ResearchParticipant, Prediction.participant_id == ResearchParticipant.id)

    if participant_id:
        query = query.filter(Prediction.participant_id == participant_id)
    if model_name:
        query = query.filter(Prediction.model_name.ilike(f"%{model_name}%"))
    if predicted_class:
        query = query.filter(Prediction.predicted_class == predicted_class)
    if search:
        s = f"%{search}%"
        query = query.filter(
            (ResearchParticipant.research_participant_code.ilike(s)) |
            (ResearchParticipant.display_name.ilike(s)) |
            (Prediction.predicted_class.ilike(s))
        )

    predictions = query.order_by(Prediction.prediction_timestamp.desc()).offset(skip).limit(limit).all()

    results = []
    for p in predictions:
        results.append({
            "id": p.id,
            "participant_id": p.participant_id,
            "participant_code": p.participant.research_participant_code if p.participant else None,
            "display_name": p.participant.display_name if p.participant else None,
            "model_name": p.model_name,
            "model_version": p.model_version,
            "predicted_class": p.predicted_class,
            "class_probabilities": p.class_probabilities or {},
            "explanation_rules": p.explanation_rules or [],
            "feature_importances": p.feature_importances or [],
            "submitted_feature_values": p.submitted_feature_values or {},
            "prediction_timestamp": p.prediction_timestamp,
            "record_status": p.record_status
        })
    return results

@router.get("/predictions/{id}", response_model=PredictionResponse)
def get_prediction(id: str, db: Session = Depends(get_db)):
    p = db.query(Prediction).filter(Prediction.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Prediction record not found")
    return {
        "id": p.id,
        "participant_id": p.participant_id,
        "participant_code": p.participant.research_participant_code if p.participant else None,
        "display_name": p.participant.display_name if p.participant else None,
        "model_name": p.model_name,
        "model_version": p.model_version,
        "predicted_class": p.predicted_class,
        "class_probabilities": p.class_probabilities or {},
        "explanation_rules": p.explanation_rules or [],
        "feature_importances": p.feature_importances or [],
        "submitted_feature_values": p.submitted_feature_values or {},
        "prediction_timestamp": p.prediction_timestamp,
        "record_status": p.record_status
    }

@router.delete("/predictions/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prediction(
    id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    p = db.query(Prediction).filter(Prediction.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Prediction record not found")
    db.delete(p)
    db.commit()
    return None

@router.get("/overview/stats", response_model=OverviewStats)
def get_overview_statistics(db: Session = Depends(get_db)):
    total_participants = db.query(ResearchParticipant).count()
    total_predictions = db.query(Prediction).count()

    # Breakdown by predicted class
    class_counts = db.query(Prediction.predicted_class, func.count(Prediction.id)).group_by(Prediction.predicted_class).all()
    class_dict = {cls: count for cls, count in class_counts}

    # Recent 5 predictions
    recent = db.query(Prediction).order_by(Prediction.prediction_timestamp.desc()).limit(5).all()
    recent_list = []
    for r in recent:
        recent_list.append({
            "id": r.id,
            "participant_code": r.participant.research_participant_code if r.participant else "N/A",
            "model_name": r.model_name,
            "predicted_class": r.predicted_class,
            "timestamp": r.prediction_timestamp.isoformat()
        })

    model_summary = {
        "sts_clinical": {
            "version": ml_service.sts_meta.get("version", "1.0.0") if ml_service.sts_meta else "N/A",
            "accuracy": ml_service.sts_meta.get("metrics", {}).get("accuracy") if ml_service.sts_meta else 0,
            "macro_f1": ml_service.sts_meta.get("metrics", {}).get("macro_f1") if ml_service.sts_meta else 0,
            "test_samples": ml_service.sts_meta.get("dataset", {}).get("test_samples") if ml_service.sts_meta else 0,
        },
        "uci_benchmark": {
            "version": ml_service.uci_meta.get("version", "1.0.0") if ml_service.uci_meta else "N/A",
            "accuracy": ml_service.uci_meta.get("metrics", {}).get("accuracy") if ml_service.uci_meta else 0,
            "macro_f1": ml_service.uci_meta.get("metrics", {}).get("macro_f1") if ml_service.uci_meta else 0,
            "test_samples": ml_service.uci_meta.get("dataset", {}).get("test_samples") if ml_service.uci_meta else 0,
        }
    }

    return {
        "total_participants": total_participants,
        "total_predictions": total_predictions,
        "active_models_count": 2 if ml_service.sts_model and ml_service.uci_model else 1,
        "predicted_classes_breakdown": class_dict,
        "recent_predictions": recent_list,
        "model_performance_summary": model_summary
    }
