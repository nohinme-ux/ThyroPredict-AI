from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from backend.app.core.config import settings
from backend.app.core.database import engine, Base, SessionLocal
from backend.app.core.security import hash_password
from backend.app.models.models import User, ResearchParticipant, Prediction
from backend.app.services.ml_service import ml_service
from backend.app.api import auth, participants, predictions, model, dataset

def seed_initial_data():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[Startup Warning] Could not auto-create database tables: {e}")
        return

    db = SessionLocal()
    try:
        # Seed researcher account if not exists
        admin_email = "researcher@thyropredict.ai"
        existing_user = db.query(User).filter(User.email == admin_email).first()
        if not existing_user:
            admin_user = User(
                email=admin_email,
                password_hash=hash_password("Research@2026"),
                role="lead_researcher"
            )
            db.add(admin_user)
            db.commit()
            print(f"[Startup] Created default research account: {admin_email}")

        # Seed sample research participants if empty
        if db.query(ResearchParticipant).count() == 0:
            sample_participants = [
                ResearchParticipant(
                    research_participant_code="THYRO-PART-001",
                    display_name="Participant Alpha",
                    age=44.0,
                    sex="F",
                    consent_status=True,
                    notes="Baseline cohort member with clinical symptoms of heat intolerance"
                ),
                ResearchParticipant(
                    research_participant_code="THYRO-PART-002",
                    display_name="Participant Beta",
                    age=56.0,
                    sex="F",
                    consent_status=True,
                    notes="Referred for fatigue and elevated cold sensitivity"
                ),
                ResearchParticipant(
                    research_participant_code="THYRO-PART-003",
                    display_name="Participant Gamma",
                    age=48.0,
                    sex="M",
                    consent_status=True,
                    notes="Routine clinical metabolic panel evaluation"
                ),
                ResearchParticipant(
                    research_participant_code="THYRO-PART-004",
                    display_name="Participant Delta (Control)",
                    age=37.0,
                    sex="F",
                    consent_status=True,
                    notes="Healthy euthyroid control participant from study cohort"
                )
            ]
            db.add_all(sample_participants)
            db.commit()
            print("[Startup] Seeded initial research participants")

            # Seed 2 initial predictions using genuine ML models
            p1 = db.query(ResearchParticipant).filter(ResearchParticipant.research_participant_code == "THYRO-PART-001").first()
            p2 = db.query(ResearchParticipant).filter(ResearchParticipant.research_participant_code == "THYRO-PART-002").first()
            
            if p1 and ml_service.sts_model:
                f1 = {
                    "AGE": 44.0, "SEX": "F", "DURATION": 4.0, "HGT": 142.0, "WGT": 51.0,
                    "bmi": 25.3, "SYS": 100.0, "DIA": 70.0, "FBS": 89.0, "FT3": 4.9,
                    "FT4": 2.12, "TSH": 0.01, "Anti tpo": 228.4, "Visfatin": 28.0,
                    "Thyroglobulin": 35.0, "IL6": 5.2, "TCHOL": 175.0, "TGL": 120.0,
                    "HDL": 52.0, "LDL": 95.0, "HB": 12.8, "WBC": 6800.0, "PLT": 250.0
                }
                res1 = ml_service.predict_sts(f1)
                pred1 = Prediction(
                    participant_id=p1.id,
                    model_name=res1["model_name"],
                    model_version=res1["model_version"],
                    submitted_feature_values=f1,
                    predicted_class=res1["predicted_class"],
                    class_probabilities=res1["class_probabilities"],
                    explanation_rules=res1["explanation_rules"],
                    feature_importances=res1["feature_importances"]
                )
                db.add(pred1)

            if p2 and ml_service.sts_model:
                f2 = {
                    "AGE": 56.0, "SEX": "F", "DURATION": 5.0, "HGT": 153.0, "WGT": 48.0,
                    "bmi": 20.5, "SYS": 120.0, "DIA": 80.0, "FBS": 92.0, "FT3": 2.65,
                    "FT4": 0.47, "TSH": 22.7, "Anti tpo": 0.11, "Visfatin": 22.0,
                    "Thyroglobulin": 15.0, "IL6": 3.8, "TCHOL": 210.0, "TGL": 140.0,
                    "HDL": 48.0, "LDL": 130.0, "HB": 13.1, "WBC": 7200.0, "PLT": 284.0
                }
                res2 = ml_service.predict_sts(f2)
                pred2 = Prediction(
                    participant_id=p2.id,
                    model_name=res2["model_name"],
                    model_version=res2["model_version"],
                    submitted_feature_values=f2,
                    predicted_class=res2["predicted_class"],
                    class_probabilities=res2["class_probabilities"],
                    explanation_rules=res2["explanation_rules"],
                    feature_importances=res2["feature_importances"]
                )
                db.add(pred2)

            db.commit()
            print("[Startup] Seeded initial verified ML predictions")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_initial_data()
    yield

app = FastAPI(
    title="ThyroPredict AI API",
    description="Decision Tree Based Thyroid Disease Research and Prediction System API",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
cors_list = settings.cors_origins
if os.getenv("CORS_ALLOW_ALL", "").lower() == "true":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(participants.router, prefix=settings.API_V1_STR)
app.include_router(predictions.router, prefix=settings.API_V1_STR)
app.include_router(model.router, prefix=settings.API_V1_STR)
app.include_router(dataset.router, prefix=settings.API_V1_STR)

@app.get("/health")
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "models_loaded": {
            "sts_clinical": ml_service.sts_model is not None,
            "uci_benchmark": ml_service.uci_model is not None
        }
    }

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs": "/docs",
        "health": "/health"
    }
