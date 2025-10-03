"""Health check endpoints."""

from typing import Dict
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..deps import get_app_components

router = APIRouter(prefix="/health", tags=["Status"])


class HealthResponse(BaseModel):
    status: str
    components: Dict[str, str]
    version: str


@router.get("", response_model=HealthResponse)
async def health_check(app_components: Dict = Depends(get_app_components)):
    """Endpoint to check if the API is running and components are loaded."""
    component_status = {}
    for name, component in app_components.items():
        component_status[name] = "loaded" if component else "failed"
    
    return HealthResponse(
        status="ok" if all(app_components.values()) else "degraded",
        components=component_status,
        version="0.1.0"
    )
