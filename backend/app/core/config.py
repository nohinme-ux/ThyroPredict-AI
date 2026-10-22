import os
import tempfile
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "ThyroPredict AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "thyropredict-super-secure-research-secret-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # Paths
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    ARTIFACTS_DIR: str = os.getenv("ARTIFACTS_DIR", os.path.join(BASE_DIR, "artifacts"))
    DATA_DIR: str = os.getenv("DATA_DIR", os.path.join(BASE_DIR, "data"))
    
    # Database (anchored to BASE_DIR, temp dir on Vercel/serverless, or cloud PostgreSQL)
    DATABASE_URL: str = (
        os.getenv("POSTGRES_URL") or
        os.getenv("DATABASE_URL") or
        (f"sqlite:///{os.path.join(tempfile.gettempdir(), 'thyropredict.db')}" if os.getenv("VERCEL") == "1" else f"sqlite:///{os.path.join(BASE_DIR, 'thyropredict.db')}")
    )

    def __init__(self, **data):
        super().__init__(**data)
        # Normalize cloud PostgreSQL URLs (e.g. Render / Supabase / Neon / Vercel using postgres://)
        if self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql://", 1)

    @property
    def cors_origins(self) -> list[str]:
        env_origins = os.getenv("CORS_ORIGINS", "")
        origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000"
        ]
        if env_origins:
            for o in env_origins.split(","):
                clean = o.strip()
                if clean and clean not in origins:
                    origins.append(clean)
        return origins

settings = Settings()
