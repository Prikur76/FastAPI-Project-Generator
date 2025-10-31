"""
Шаблоны для Layered Architecture.
"""

LAYERED_TEMPLATES = {
    "main": """\
from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.session import engine, Base

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )
    
    # Создание таблиц БД
    Base.metadata.create_all(bind=engine)
    
    # Подключение роутеров
    application.include_router(api_router, prefix=settings.API_V1_STR)
    
    return application

app = create_application()

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI with Layered Architecture!"}
""",

    "config": """\
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "{{ project_slug }}"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./{{ project_slug }}.db"
    
    class Config:
        case_sensitive = True

settings = Settings()
""",

    "model": """\
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class {{ class_name }}(Base):
    __tablename__ = "{{ table_name }}"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<{{ class_name }}(id={self.id})>"
""",

    "schema": """\
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class {{ class_name }}Base(BaseModel):
    pass

class {{ class_name }}Create({{ class_name }}Base):
    pass

class {{ class_name }}Update({{ class_name }}Base):
    pass

class {{ class_name }}({{ class_name }}Base):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
""",

    "service": """\
from typing import List, Optional
from app.repositories.{{ module_name }}_repository import {{ class_name }}Repository
from app.schemas.{{ module_name }} import {{ class_name }}Create, {{ class_name }}Update

class {{ class_name }}Service:
    def __init__(self, {{ module_name }}_repository: {{ class_name }}Repository):
        self.{{ module_name }}_repository = {{ module_name }}_repository
    
    def get_{{ module_name }}(self, {{ module_name }}_id: int):
        return self.{{ module_name }}_repository.get_by_id({{ module_name }}_id)
    
    def get_all_{{ module_name }}s(self, skip: int = 0, limit: int = 100):
        return self.{{ module_name }}_repository.get_all(skip=skip, limit=limit)
    
    def create_{{ module_name }}(self, {{ module_name }}_create: {{ class_name }}Create):
        return self.{{ module_name }}_repository.create({{ module_name }}_create)
    
    def update_{{ module_name }}(self, {{ module_name }}_id: int, {{ module_name }}_update: {{ class_name }}Update):
        return self.{{ module_name }}_repository.update({{ module_name }}_id, {{ module_name }}_update)
    
    def delete_{{ module_name }}(self, {{ module_name }}_id: int):
        return self.{{ module_name }}_repository.delete({{ module_name }}_id)
""",

    "repository": """\
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.{{ module_name }} import {{ class_name }}
from app.schemas.{{ module_name }} import {{ class_name }}Create, {{ class_name }}Update

class {{ class_name }}Repository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, {{ module_name }}_id: int) -> Optional[{{ class_name }}]:
        return self.db.query({{ class_name }}).filter({{ class_name }}.id == {{ module_name }}_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[{{ class_name }}]:
        return self.db.query({{ class_name }}).offset(skip).limit(limit).all()
    
    def create(self, {{ module_name }}_create: {{ class_name }}Create) -> {{ class_name }}:
        db_{{ module_name }} = {{ class_name }}(**{{ module_name }}_create.dict())
        self.db.add(db_{{ module_name }})
        self.db.commit()
        self.db.refresh(db_{{ module_name }})
        return db_{{ module_name }}
    
    def update(self, {{ module_name }}_id: int, {{ module_name }}_update: {{ class_name }}Update) -> Optional[{{ class_name }}]:
        db_{{ module_name }} = self.get_by_id({{ module_name }}_id)
        if db_{{ module_name }}:
            update_data = {{ module_name }}_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_{{ module_name }}, field, value)
            self.db.commit()
            self.db.refresh(db_{{ module_name }})
        return db_{{ module_name }}
    
    def delete(self, {{ module_name }}_id: int) -> bool:
        db_{{ module_name }} = self.get_by_id({{ module_name }}_id)
        if db_{{ module_name }}:
            self.db.delete(db_{{ module_name }})
            self.db.commit()
            return True
        return False
""",

    "router": """\
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.{{ module_name }} import {{ class_name }}, {{ class_name }}Create, {{ class_name }}Update
from app.services.{{ module_name }}_service import {{ class_name }}Service
from app.repositories.{{ module_name }}_repository import {{ class_name }}Repository
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model={{ class_name }})
def create_{{ module_name }}(
    {{ module_name }}: {{ class_name }}Create, 
    db: Session = Depends(get_db)
):
    {{ module_name }}_repo = {{ class_name }}Repository(db)
    {{ module_name }}_service = {{ class_name }}Service({{ module_name }}_repo)
    return {{ module_name }}_service.create_{{ module_name }}({{ module_name }})

@router.get("/{ {{ module_name }}_id}", response_model={{ class_name }})
def read_{{ module_name }}(
    {{ module_name }}_id: int, 
    db: Session = Depends(get_db)
):
    {{ module_name }}_repo = {{ class_name }}Repository(db)
    {{ module_name }}_service = {{ class_name }}Service({{ module_name }}_repo)
    db_{{ module_name }} = {{ module_name }}_service.get_{{ module_name }}({{ module_name }}_id)
    if db_{{ module_name }} is None:
        raise HTTPException(status_code=404, detail="{{ class_name }} not found")
    return db_{{ module_name }}

@router.get("/", response_model=List[{{ class_name }}])
def read_{{ module_name }}s(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    {{ module_name }}_repo = {{ class_name }}Repository(db)
    {{ module_name }}_service = {{ class_name }}Service({{ module_name }}_repo)
    return {{ module_name }}_service.get_all_{{ module_name }}s(skip=skip, limit=limit)

@router.put("/{ {{ module_name }}_id}", response_model={{ class_name }})
def update_{{ module_name }}(
    {{ module_name }}_id: int, 
    {{ module_name }}: {{ class_name }}Update, 
    db: Session = Depends(get_db)
):
    {{ module_name }}_repo = {{ class_name }}Repository(db)
    {{ module_name }}_service = {{ class_name }}Service({{ module_name }}_repo)
    return {{ module_name }}_service.update_{{ module_name }}({{ module_name }}_id, {{ module_name }})

@router.delete("/{ {{ module_name }}_id}")
def delete_{{ module_name }}(
    {{ module_name }}_id: int, 
    db: Session = Depends(get_db)
):
    {{ module_name }}_repo = {{ class_name }}Repository(db)
    {{ module_name }}_service = {{ class_name }}Service({{ module_name }}_repo)
    success = {{ module_name }}_service.delete_{{ module_name }}({{ module_name }}_id)
    if not success:
        raise HTTPException(status_code=404, detail="{{ class_name }} not found")
    return {"message": "{{ class_name }} deleted successfully"}
""",

    "database": """\
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",

    "api_router": """\
from fastapi import APIRouter
from app.api.v1.endpoints import {{ module_name }}

api_router = APIRouter()
api_router.include_router({{ module_name }}.router, prefix="/{{ module_name }}s", tags=["{{ module_name }}s"])
"""
}