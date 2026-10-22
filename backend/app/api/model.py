from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import subprocess
import os

from backend.app.services.ml_service import ml_service
from backend.app.core.config import settings

router = APIRouter(prefix="/model", tags=["Model Information & Metrics"])

@router.get("/info")
def get_models_info():
    return {
        "active_models": [
            {
                "id": "sts_clinical",
                "name": "STS Clinical Decision Tree Classifier",
                "version": ml_service.sts_meta.get("version", "1.0.0") if ml_service.sts_meta else "N/A",
                "algorithm": "DecisionTreeClassifier (scikit-learn)",
                "dataset_name": "STS Clinical Thyroid Study (sts thyroid data.xlsx)",
                "classes": ml_service.sts_meta.get("classes", []) if ml_service.sts_meta else [],
                "feature_count": len(ml_service.sts_meta.get("features", {}).get("numeric", [])) + len(ml_service.sts_meta.get("features", {}).get("categorical", [])) if ml_service.sts_meta else 0,
                "training_timestamp": ml_service.sts_meta.get("training_timestamp") if ml_service.sts_meta else None
            },
            {
                "id": "uci_benchmark",
                "name": "UCI Benchmark Decision Tree Classifier",
                "version": ml_service.uci_meta.get("version", "1.0.0") if ml_service.uci_meta else "N/A",
                "algorithm": "DecisionTreeClassifier (scikit-learn)",
                "dataset_name": "UCI Thyroid Disease Benchmark (allhypo)",
                "classes": ml_service.uci_meta.get("classes", []) if ml_service.uci_meta else [],
                "feature_count": len(ml_service.uci_meta.get("features", {}).get("numeric", [])) + len(ml_service.uci_meta.get("features", {}).get("boolean", [])) + len(ml_service.uci_meta.get("features", {}).get("categorical", [])) if ml_service.uci_meta else 0,
                "training_timestamp": ml_service.uci_meta.get("training_timestamp") if ml_service.uci_meta else None
            }
        ]
    }

@router.get("/metrics")
def get_model_metrics(model_id: str = "sts_clinical"):
    if model_id == "sts_clinical":
        if not ml_service.sts_meta:
            raise HTTPException(status_code=404, detail="STS Model metadata not found")
        return ml_service.sts_meta
    elif model_id == "uci_benchmark":
        if not ml_service.uci_meta:
            raise HTTPException(status_code=404, detail="UCI Model metadata not found")
        return ml_service.uci_meta
    else:
        raise HTTPException(status_code=400, detail=f"Unknown model_id: {model_id}")

@router.post("/retrain")
def retrain_models():
    """Trigger retrain script and reload artifacts."""
    try:
        scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "scripts"))
        sts_script = os.path.join(scripts_dir, "train_sts_model.py")
        uci_script = os.path.join(scripts_dir, "train_uci_model.py")
        
        res1 = subprocess.run(["python", sts_script], capture_output=True, text=True, check=True)
        res2 = subprocess.run(["python", uci_script], capture_output=True, text=True, check=True)
        
        ml_service.load_models()
        return {
            "status": "success",
            "message": "Models retrained and reloaded successfully",
            "sts_accuracy": ml_service.sts_meta.get("metrics", {}).get("accuracy"),
            "uci_accuracy": ml_service.uci_meta.get("metrics", {}).get("accuracy")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(e)}")
