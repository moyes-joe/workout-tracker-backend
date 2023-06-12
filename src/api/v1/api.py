from fastapi import APIRouter

from src.api.v1.endpoints import health_check, workout_log, workout_plans

api_router = APIRouter()
api_router.include_router(
    health_check.router, prefix="/health-check", tags=["health_check"]
)
api_router.include_router(workout_plans.router, prefix="/plans", tags=["workout_plans"])
api_router.include_router(workout_log.router, prefix="/logs", tags=["workout_logs"])
