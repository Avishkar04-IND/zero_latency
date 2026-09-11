from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    auth,
    organizations,
    branches,
    medicines,
    batches,
    codes,
    verification,
    scans,
    accessibility,
    analytics,
    layouts,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(organizations.router)
api_router.include_router(branches.router)
api_router.include_router(medicines.router)
api_router.include_router(batches.router)
api_router.include_router(codes.router)
api_router.include_router(verification.router)
api_router.include_router(scans.router)
api_router.include_router(accessibility.router)
api_router.include_router(analytics.router)
api_router.include_router(layouts.router)
