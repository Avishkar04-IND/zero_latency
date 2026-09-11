"""
Smart Medicine Platform — Pharmaceutical Layout Optimizer Engine
Member 3 Core Ownership
"""
from typing import Any, Dict, List
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.layouts import router as layouts_router

app = FastAPI(
    title="Pharmaceutical Layout Optimizer Engine",
    description="Microservice for package dimension calculations, print area optimization, QR/DataMatrix placement, and preview generation.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(layouts_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Consistent, structured request validation error handler without leaking internal details."""
    errors: List[str] = []
    sanitized_details = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []))
        msg = str(err.get("msg", "Invalid input"))
        errors.append(f"{field}: {msg}")
        sanitized_details.append({
            "loc": [str(loc) for loc in err.get("loc", [])],
            "msg": msg,
            "type": str(err.get("type", "value_error")),
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed. Verify physical dimensions and constraints.",
                "details": errors,
            },
            "detail": sanitized_details,
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Consistent HTTP exception handler ensuring structured error format."""
    detail = exc.detail
    message = detail if isinstance(detail, str) else "HTTP request error occurred."
    details = [detail] if isinstance(detail, str) else (detail.get("errors", []) if isinstance(detail, dict) else [])
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": message,
                "details": details,
            },
            "detail": detail,
        },
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
