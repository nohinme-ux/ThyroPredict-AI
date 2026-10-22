import os
import sys
import uuid

sys.path.insert(0, os.path.abspath("."))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models.models import Base, User, ResearchParticipant, Prediction
from backend.app.core.security import hash_password, verify_password

SANDBOX_DB = "data/test_persistence_sandbox.db"
if os.path.exists(SANDBOX_DB):
    os.remove(SANDBOX_DB)

print("=" * 60)
print("ISOLATED DATABASE PERSISTENCE & PROCESS RESTART VERIFICATION")
print("=" * 60)

# 1. Initialize fresh sandbox database
engine1 = create_engine(f"sqlite:///{SANDBOX_DB}")
Base.metadata.create_all(bind=engine1)
Session1 = sessionmaker(bind=engine1)
db1 = Session1()

# 2. Insert synthetic entities
user_id = str(uuid.uuid4())
test_user = User(
    id=user_id,
    email="test_researcher@sandbox.local",
    password_hash=hash_password("SandboxSecurePassword123!"),
    role="researcher"
)
db1.add(test_user)

participant_id = str(uuid.uuid4())
test_participant = ResearchParticipant(
    id=participant_id,
    research_participant_code="SANDBOX-PART-001",
    display_name="Sandbox Subject Omega",
    age=47.0,
    sex="F",
    consent_status=True,
    notes="Isolated persistence test subject"
)
db1.add(test_participant)
db1.commit()

prediction_id = str(uuid.uuid4())
features_payload = {
    "AGE": 47.0, "SEX": "F", "TSH": 34.5, "Anti_tpo": 4.5, "FT4": 0.6
}
test_prediction = Prediction(
    id=prediction_id,
    participant_id=participant_id,
    created_by_user_id=user_id,
    model_name="STS Clinical Decision Tree",
    model_version="1.0.0",
    submitted_feature_values=features_payload,
    predicted_class="Primary Hypothyroidism",
    class_probabilities={"Primary Hypothyroidism": 1.0, "Euthyroid / Normal": 0.0},
    explanation_rules=["Decision Node 0: Anti tpo (4.50) <= 37.50 -> Left", "Decision Node 1: TSH (34.50) > 0.58 -> Right"],
    record_status="active"
)
db1.add(test_prediction)
db1.commit()
db1.close()

# 3. Simulate COMPLETE PROCESS SHUTDOWN
engine1.dispose()
print(f"Sandbox DB created ({SANDBOX_DB}) and populated. Process 1 terminated.")

# 4. Simulate FRESH APPLICATION RESTART (Process 2)
engine2 = create_engine(f"sqlite:///{SANDBOX_DB}")
Session2 = sessionmaker(bind=engine2)
db2 = Session2()

# 5. Retrieve saved entities in Process 2
retrieved_p = db2.query(ResearchParticipant).filter(ResearchParticipant.id == participant_id).first()
assert retrieved_p is not None, "Participant did not survive restart!"
assert retrieved_p.research_participant_code == "SANDBOX-PART-001"
print(f"Process 2: Retrieved Participant '{retrieved_p.research_participant_code}' - SUCCESS.")

retrieved_pred = db2.query(Prediction).filter(Prediction.id == prediction_id).first()
assert retrieved_pred is not None, "Prediction record did not survive restart!"
assert retrieved_pred.predicted_class == "Primary Hypothyroidism"
assert retrieved_pred.submitted_feature_values["TSH"] == 34.5
assert len(retrieved_pred.explanation_rules) == 2
print(f"Process 2: Retrieved Prediction '{retrieved_pred.id}' with exact features & rules - SUCCESS.")

# 6. Verify password hashing security (plaintext password is never stored)
user_retrieved = db2.query(User).filter(User.id == user_id).first()
assert user_retrieved.password_hash != "SandboxSecurePassword123!"
assert verify_password("SandboxSecurePassword123!", user_retrieved.password_hash)
print("Process 2: Verified password hashing security (bcrypt) - SUCCESS.")

# 7. Test Cascade Deletion
db2.delete(retrieved_p)
db2.commit()

# Verify prediction was cascade deleted
check_pred = db2.query(Prediction).filter(Prediction.id == prediction_id).first()
assert check_pred is None, "Cascade delete failed!"
print("Process 2: Verified cascade deletion - SUCCESS.")

db2.close()
engine2.dispose()

# Clean up sandbox file
if os.path.exists(SANDBOX_DB):
    os.remove(SANDBOX_DB)
print("Cleaned up sandbox database file.")
print("\nIsolated Persistence & Restart Verification: ALL CHECKS PASSED.")
