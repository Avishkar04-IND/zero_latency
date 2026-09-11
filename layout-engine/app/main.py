"""
Smart Medicine Platform — Pharmaceutical Layout Optimizer Engine
Member 3 Core Ownership
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Pharmaceutical Layout Optimizer Engine",
    description="Standalone microservice for package dimension calculations, print area optimization, QR/DataMatrix placement, and preview generation.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "service": "layout-optimizer-engine",
        "version": "0.1.0",
        "message": "Pharmaceutical Layout Optimizer Engine service initialized."
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
