from fastapi import FastAPI

from app.api.asset import router as asset_router
from app.api.environment import router as environment_router
from app.api.health import router as health_router
from app.api.service import router as service_router
from app.api.team import router as team_router
from app.config.settings import settings


app = FastAPI(title=settings.app_name)
app.include_router(health_router)
app.include_router(environment_router)
app.include_router(team_router)
app.include_router(service_router)
app.include_router(asset_router)


if __name__ == "__main__":
    print(f"{settings.app_name} runtime skeleton")
