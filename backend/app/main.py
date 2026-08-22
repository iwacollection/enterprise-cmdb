from fastapi import FastAPI

from app.api.health import router as health_router
from app.config.settings import settings


app = FastAPI(title=settings.app_name)
app.include_router(health_router)


if __name__ == "__main__":
    print(f"{settings.app_name} runtime skeleton")
