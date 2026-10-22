from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
import os
import json
import csv
import io

try:
    import pandas as pd
except ImportError:
    pd = None

from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.models.models import Prediction, ResearchParticipant

router = APIRouter(prefix="", tags=["Dataset & Research Export"])

@router.get("/dataset/summary")
def get_dataset_summary():
    dict_path = os.path.join(settings.DATA_DIR, "dataset_dictionary.json")
    sts_clean_path = os.path.join(settings.DATA_DIR, "sts_cleaned.csv")
    uci_train_path = os.path.join(settings.DATA_DIR, "uci_train.csv")

    summary = {
        "dictionary": {},
        "sts_stats": {},
        "uci_stats": {}
    }

    if os.path.exists(dict_path):
        with open(dict_path, "r", encoding="utf-8") as f:
            summary["dictionary"] = json.load(f)

    if os.path.exists(sts_clean_path):
        if pd is not None:
            sts_df = pd.read_csv(sts_clean_path)
            summary["sts_stats"] = {
                "total_records": len(sts_df),
                "class_distribution": sts_df["target"].value_counts().to_dict(),
                "numerical_summary": {
                    col: {
                        "mean": round(float(sts_df[col].mean()), 2),
                        "std": round(float(sts_df[col].std()), 2),
                        "min": round(float(sts_df[col].min()), 2),
                        "max": round(float(sts_df[col].max()), 2)
                    }
                    for col in ["AGE", "TSH", "FT3", "FT4", "Anti tpo", "bmi", "SYS", "DIA"]
                    if col in sts_df.columns and pd.api.types.is_numeric_dtype(sts_df[col])
                }
            }
        else:
            with open(sts_clean_path, "r", encoding="utf-8") as f:
                reader = list(csv.DictReader(f))
                classes = {}
                for r in reader:
                    t = r.get("target")
                    if t:
                        classes[t] = classes.get(t, 0) + 1
                summary["sts_stats"] = {
                    "total_records": len(reader),
                    "class_distribution": classes,
                    "numerical_summary": {}
                }

    if os.path.exists(uci_train_path):
        if pd is not None:
            uci_df = pd.read_csv(uci_train_path)
            summary["uci_stats"] = {
                "train_records": len(uci_df),
                "class_distribution": uci_df["target"].value_counts().to_dict(),
            }
        else:
            with open(uci_train_path, "r", encoding="utf-8") as f:
                reader = list(csv.DictReader(f))
                classes = {}
                for r in reader:
                    t = r.get("target")
                    if t:
                        classes[t] = classes.get(t, 0) + 1
                summary["uci_stats"] = {
                    "train_records": len(reader),
                    "class_distribution": classes,
                }

    return summary

@router.get("/research/export")
def export_research_records(
    anonymize: bool = True,
    db: Session = Depends(get_db)
):
    """Export saved prediction records as CSV for research audit."""
    predictions = db.query(Prediction).join(ResearchParticipant).order_by(Prediction.prediction_timestamp.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    header = [
        "Record_ID",
        "Participant_Code" if not anonymize else "Deidentified_Participant_ID",
        "Prediction_Timestamp",
        "Model_Name",
        "Model_Version",
        "Predicted_Class",
        "Confidence_Score",
        "Key_Explanations",
        "Submitted_Features_JSON"
    ]
    writer.writerow(header)

    for p in predictions:
        probs = p.class_probabilities or {}
        confidence = probs.get(p.predicted_class, 1.0)
        rules_text = " | ".join(p.explanation_rules or [])
        features_json = json.dumps(p.submitted_feature_values or {})

        p_code = p.participant.research_participant_code if p.participant else "UNKNOWN"
        if anonymize:
            p_code = f"ANON-{str(p.participant_id)[:8].upper()}"

        writer.writerow([
            p.id,
            p_code,
            p.prediction_timestamp.isoformat(),
            p.model_name,
            p.model_version,
            p.predicted_class,
            f"{confidence:.4f}",
            rules_text,
            features_json
        ])

    output.seek(0)
    filename = f"thyropredict_export_{'anonymized' if anonymize else 'full'}.csv"
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
