from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.asset import router as asset_router
from app.api.audit import router as audit_router
from app.api.environment import router as environment_router
from app.api.health import router as health_router
from app.api.relation import router as relation_router
from app.api.service import router as service_router
from app.api.team import router as team_router
from app.config.settings import settings


app = FastAPI(title=settings.app_name)
app.include_router(health_router)
app.include_router(environment_router)
app.include_router(team_router)
app.include_router(service_router)
app.include_router(asset_router)
app.include_router(relation_router)
app.include_router(audit_router)
app.mount("/ui", StaticFiles(directory=Path(__file__).with_name("web"), html=True), name="ui")


@app.get("/", include_in_schema=False)
def web_console():
    return RedirectResponse(url="/ui/")


if __name__ == "__main__":
    print(f"{settings.app_name} runtime skeleton")
