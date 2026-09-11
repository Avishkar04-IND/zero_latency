"""
Smart Medicine Platform — Backend API Service
Member 1 Core Ownership
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Smart Medicine Platform — Core Backend API",
    description="FastAPI service handling DB, authentication, medicine management, batch codes, and verification.",
    version="0.1.0",
)

# Configure CORS
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
        "service": "smart-medicine-backend",
        "version": "0.1.0",
        "message": "Smart Medicine Platform Core Backend Service is initialized."
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
