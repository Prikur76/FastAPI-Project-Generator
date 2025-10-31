"""
Шаблоны для Modular Architecture.
"""

MODULAR_TEMPLATES = {
    "main": """\
from fastapi import FastAPI
from app.database import engine, Base

# Создание таблиц
Base.metadata.create_all(bind=engine)

app = FastAPI(title="{{ project_slug }}")

# Импортируйте и подключите роутеры здесь
# from app.routers import {{ module_name }}
# app.include_router({{ module_name }}.router, prefix="/{{ module_name }}s", tags=["{{ module_name }}s"])

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI with Modular Architecture!"}
""",

    "model": """\
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
from datetime import datetime

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

    "router": """\
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.{{ class_name }})
def create_{{ module_name }}(
    {{ module_name }}: schemas.{{ class_name }}Create, 
    db: Session = Depends(get_db)
):
    db_{{ module_name }} = models.{{ class_name }}(**{{ module_name }}.dict())
    db.add(db_{{ module_name }})
    db.commit()
    db.refresh(db_{{ module_name }})
    return db_{{ module_name }}

@router.get("/{ {{ module_name }}_id}", response_model=schemas.{{ class_name }})
def read_{{ module_name }}(
    {{ module_name }}_id: int, 
    db: Session = Depends(get_db)
):
    {{ module_name }} = db.query(models.{{ class_name }}).filter(
        models.{{ class_name }}.id == {{ module_name }}_id
    ).first()
    if {{ module_name }} is None:
        raise HTTPException(status_code=404, detail="{{ class_name }} not found")
    return {{ module_name }}

@router.get("/", response_model=List[schemas.{{ class_name }}])
def read_{{ module_name }}s(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    {{ module_name }}s = db.query(models.{{ class_name }}).offset(skip).limit(limit).all()
    return {{ module_name }}s

@router.put("/{ {{ module_name }}_id}", response_model=schemas.{{ class_name }})
def update_{{ module_name }}(
    {{ module_name }}_id: int, 
    {{ module_name }}: schemas.{{ class_name }}Update, 
    db: Session = Depends(get_db)
):
    db_{{ module_name }} = db.query(models.{{ class_name }}).filter(
        models.{{ class_name }}.id == {{ module_name }}_id
    ).first()
    if db_{{ module_name }} is None:
        raise HTTPException(status_code=404, detail="{{ class_name }} not found")
    
    update_data = {{ module_name }}.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_{{ module_name }}, field, value)
    
    db.commit()
    db.refresh(db_{{ module_name }})
    return db_{{ module_name }}

@router.delete("/{ {{ module_name }}_id}")
def delete_{{ module_name }}(
    {{ module_name }}_id: int, 
    db: Session = Depends(get_db)
):
    db_{{ module_name }} = db.query(models.{{ class_name }}).filter(
        models.{{ class_name }}.id == {{ module_name }}_id
    ).first()
    if db_{{ module_name }} is None:
        raise HTTPException(status_code=404, detail="{{ class_name }} not found")
    
    db.delete(db_{{ module_name }})
    db.commit()
    return {"message": "{{ class_name }} deleted successfully"}
""",

    "database": """\
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./{{ project_slug }}.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
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

    "crud": """\
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas

class {{ class_name }}CRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def get(self, {{ module_name }}_id: int) -> Optional[models.{{ class_name }}]:
        return self.db.query(models.{{ class_name }}).filter(
            models.{{ class_name }}.id == {{ module_name }}_id
        ).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[models.{{ class_name }}]:
        return self.db.query(models.{{ class_name }}).offset(skip).limit(limit).all()
    
    def create(self, {{ module_name }}: schemas.{{ class_name }}Create) -> models.{{ class_name }}:
        db_{{ module_name }} = models.{{ class_name }}(**{{ module_name }}.dict())
        self.db.add(db_{{ module_name }})
        self.db.commit()
        self.db.refresh(db_{{ module_name }})
        return db_{{ module_name }}
    
    def update(self, {{ module_name }}_id: int, {{ module_name }}: schemas.{{ class_name }}Update) -> Optional[models.{{ class_name }}]:
        db_{{ module_name }} = self.get({{ module_name }}_id)
        if db_{{ module_name }}:
            update_data = {{ module_name }}.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_{{ module_name }}, field, value)
            self.db.commit()
            self.db.refresh(db_{{ module_name }})
        return db_{{ module_name }}
    
    def delete(self, {{ module_name }}_id: int) -> bool:
        db_{{ module_name }} = self.get({{ module_name }}_id)
        if db_{{ module_name }}:
            self.db.delete(db_{{ module_name }})
            self.db.commit()
            return True
        return False
""",

    "dependencies": """\
from app.database import get_db
from app.crud.{{ module_name }} import {{ class_name }}CRUD

def get_{{ module_name }}_crud(db = Depends(get_db)):
    return {{ class_name }}CRUD(db)
"""
}
