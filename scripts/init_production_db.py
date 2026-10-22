import os
import sys

# Ensure backend modules can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.models.models import User, ResearchParticipant, Prediction, ModelVersionRecord
from backend.app.main import seed_initial_data

def init_db():
    print(f"Connecting to target database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    print("Creating tables if they do not exist...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
    print("Seeding initial administrator and baseline research cohort...")
    seed_initial_data()
    print("Database schema initialization and baseline seeding complete!")

if __name__ == "__main__":
    init_db()
