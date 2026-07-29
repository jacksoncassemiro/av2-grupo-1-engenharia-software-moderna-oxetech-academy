from fastapi import FastAPI
from app.database import Base, engine

# Create tables in DB (for development/MVP)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Gestão de Clínica Médica (MVP)",
    description="API Backend para gestão de clínica médica",
    version="0.1.0"
)

@app.get("/")
def read_root():
    return {
        "message": "API da Clínica Médica operacional!",
        "status": "online"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "postgresql"
    }
