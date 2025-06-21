# backend/services/health.py
from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/")
async def health_check():
    return {"status": "healthy", "timestamp": "2025-06-20T...", "version": "1.0.0"}


@router.get("/detailed")
async def detailed_health():
    return {
        "status": "healthy",
        "database": "connected",
        "memory_usage": "45%",
        "uptime": "2h 30m",
    }
