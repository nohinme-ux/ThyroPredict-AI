from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Auth Schemas ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Optional[str] = "researcher"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: EmailStr
    role: str
    account_status: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

# --- Research Participant Schemas ---
class ParticipantCreate(BaseModel):
    research_participant_code: str = Field(..., min_length=2, max_length=100)
    display_name: Optional[str] = None
    age: Optional[float] = None
    sex: Optional[str] = "F"
    consent_status: bool = True
    notes: Optional[str] = None

class ParticipantUpdate(BaseModel):
    display_name: Optional[str] = None
    age: Optional[float] = None
    sex: Optional[str] = None
    consent_status: Optional[bool] = None
    notes: Optional[str] = None

class ParticipantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    research_participant_code: str
    display_name: Optional[str] = None
    age: Optional[float] = None
    sex: Optional[str] = None
    consent_status: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    prediction_count: Optional[int] = 0

# --- Prediction Input Schemas ---
class STSPredictionInput(BaseModel):
    AGE: float = Field(..., ge=1, le=120, description="Age in years")
    SEX: str = Field("F", pattern="^(F|M)$", description="Biological sex (F/M)")
    DURATION: Optional[float] = Field(0.0, ge=0, description="Duration of symptoms/disease in years (0 for new/control)")
    HGT: Optional[float] = Field(155.0, ge=50, le=250, description="Height in cm")
    WGT: Optional[float] = Field(60.0, ge=20, le=250, description="Weight in kg")
    bmi: Optional[float] = Field(24.0, ge=10, le=60, description="BMI in kg/m^2")
    SYS: Optional[float] = Field(120.0, ge=70, le=250, description="Systolic blood pressure (mmHg)")
    DIA: Optional[float] = Field(80.0, ge=40, le=150, description="Diastolic blood pressure (mmHg)")
    FBS: Optional[float] = Field(95.0, ge=40, le=500, description="Fasting blood sugar (mg/dL)")
    FT3: float = Field(..., ge=0.1, le=20.0, description="Free T3 in pg/mL")
    FT4: float = Field(..., ge=0.01, le=15.0, description="Free T4 in ng/dL")
    TSH: float = Field(..., ge=0.0001, le=300.0, description="Serum TSH in uIU/mL")
    Anti_tpo: float = Field(..., ge=0.0, le=2000.0, description="Anti-TPO antibody titer in IU/mL")
    Visfatin: Optional[float] = Field(25.0, ge=0.0, le=200.0, description="Serum Visfatin in ng/mL")
    Thyroglobulin: Optional[float] = Field(20.0, ge=0.0, le=500.0, description="Thyroglobulin in ng/mL")
    IL6: Optional[float] = Field(4.0, ge=0.0, le=100.0, description="Interleukin-6 in pg/mL")
    TCHOL: Optional[float] = Field(180.0, ge=50, le=500, description="Total Cholesterol in mg/dL")
    TGL: Optional[float] = Field(130.0, ge=30, le=600, description="Triglycerides in mg/dL")
    HDL: Optional[float] = Field(45.0, ge=10, le=120, description="HDL cholesterol in mg/dL")
    LDL: Optional[float] = Field(100.0, ge=20, le=350, description="LDL cholesterol in mg/dL")
    HB: Optional[float] = Field(13.0, ge=4, le=22, description="Hemoglobin in g/dL")
    WBC: Optional[float] = Field(7000.0, ge=1000, le=30000, description="WBC count in cells/uL")
    PLT: Optional[float] = Field(250.0, ge=10, le=1000, description="Platelets in 10^3/uL")

class UCIPredictionInput(BaseModel):
    age: float = Field(..., ge=1, le=120)
    sex: str = Field("F", pattern="^(F|M)$")
    on_thyroxine: bool = False
    query_on_thyroxine: bool = False
    on_antithyroid_medication: bool = False
    sick: bool = False
    pregnant: bool = False
    thyroid_surgery: bool = False
    I131_treatment: bool = False
    query_hypothyroid: bool = False
    query_hyperthyroid: bool = False
    lithium: bool = False
    goitre: bool = False
    tumor: bool = False
    hypopituitary: bool = False
    psych: bool = False
    TSH: float = Field(..., ge=0.0001, le=300.0)
    T3: Optional[float] = Field(2.0, ge=0.0, le=20.0)
    TT4: Optional[float] = Field(100.0, ge=0.0, le=500.0)
    T4U: Optional[float] = Field(1.0, ge=0.1, le=3.0)
    FTI: Optional[float] = Field(100.0, ge=0.0, le=500.0)

class PredictionRequest(BaseModel):
    participant_id: str
    model_type: str = Field("sts_clinical", pattern="^(sts_clinical|uci_benchmark)$")
    sts_features: Optional[STSPredictionInput] = None
    uci_features: Optional[UCIPredictionInput] = None

class PredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    participant_id: str
    participant_code: Optional[str] = None
    display_name: Optional[str] = None
    model_name: str
    model_version: str
    predicted_class: str
    class_probabilities: Dict[str, float]
    explanation_rules: List[str]
    feature_importances: List[Dict[str, Any]]
    submitted_feature_values: Dict[str, Any]
    prediction_timestamp: datetime
    record_status: str

# --- Analytics / Dashboard Schemas ---
class OverviewStats(BaseModel):
    total_participants: int
    total_predictions: int
    active_models_count: int
    predicted_classes_breakdown: Dict[str, int]
    recent_predictions: List[Dict[str, Any]]
    model_performance_summary: Dict[str, Any]
