"""
Конфигурация и шаблоны для генератора.
"""

LAYERED_TEMPLATES = {
    "main": """from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.session import engine, Base

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )
    Base.metadata.create_all(bind=engine)
    application.include_router(api_router, prefix=settings.API_V1_STR)
    return application

app = create_application()
""",
    "config": """from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "{{ project_slug }}"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./{{ project_slug }}.db"
    
    class Config:
        case_sensitive = True

settings = Settings()
""",
    # ... остальные шаблоны для layered архитектуры
}

CLEAN_TEMPLATES = {
    "main": """from fastapi import FastAPI
from src.infrastructure.web.fastapi_app import create_app
from src.infrastructure.database.database import get_db
from src.infrastructure.database.user_repository import SQLAlchemyUserRepository

# Composition Root
db = next(get_db())
user_repository = SQLAlchemyUserRepository(db)

app = create_app(user_repository)
""",
    # ... остальные шаблоны для clean архитектуры
}

MODULAR_TEMPLATES = {
    "main": """from fastapi import FastAPI
from app.database import engine, Base

Base.metadata.create_all(bind=engine)
app = FastAPI(title="{{ project_slug }}")

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}
""",
    # ... остальные шаблоны для modular архитектуры
}

TEMPLATES = {
    "layered": LAYERED_TEMPLATES,
    "clean": CLEAN_TEMPLATES, 
    "modular": MODULAR_TEMPLATES
}

ARCHITECTURE_STRUCTURES = {
    "layered": """
project/
├── app/
│   ├── api/v1/endpoints/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── repositories/
│   └── db/
├── tests/
└── pyproject.toml
""",
    "clean": """
project/
├── src/
│   ├── domain/entities/
│   ├── domain/repositories/
│   ├── application/use_cases/
│   ├── infrastructure/database/
│   ├── infrastructure/web/
│   └── interface_adapters/
├── tests/
└── pyproject.toml
""",
    "modular": """
project/
├── app/
│   ├── routers/
│   ├── models/
│   ├── database/
│   └── dependencies/
├── tests/
└── main.py
"""
}