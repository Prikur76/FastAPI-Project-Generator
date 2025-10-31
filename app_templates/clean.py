"""
Шаблоны для Clean Architecture.
"""

CLEAN_TEMPLATES = {
    "main": """\
from fastapi import FastAPI
from src.infrastructure.web.fastapi_app import create_app
from src.infrastructure.database.database import get_db
from src.infrastructure.database.{{ module_name }}_repository import SQLAlchemy{{ class_name }}Repository
from src.application.use_cases.create_{{ module_name }} import Create{{ class_name }}UseCase
from src.application.use_cases.get_{{ module_name }} import Get{{ class_name }}UseCase

# Composition Root
db = next(get_db())
{{ module_name }}_repository = SQLAlchemy{{ class_name }}Repository(db)
create_{{ module_name }}_use_case = Create{{ class_name }}UseCase({{ module_name }}_repository)
get_{{ module_name }}_use_case = Get{{ class_name }}UseCase({{ module_name }}_repository)

app = create_app(create_{{ module_name }}_use_case, get_{{ module_name }}_use_case)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
""",

    "domain_entity": """\
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class {{ class_name }}:
    id: Optional[int] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f"{{ class_name }}(id={{self.id}})"
""",

    "domain_repository": """\
from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.{{ module_name }} import {{ class_name }}

class {{ class_name }}Repository(ABC):
    @abstractmethod
    def save(self, {{ module_name }}: {{ class_name }}) -> {{ class_name }}:
        pass
    
    @abstractmethod
    def get_by_id(self, {{ module_name }}_id: int) -> Optional[{{ class_name }}]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[{{ class_name }}]:
        pass
    
    @abstractmethod
    def delete(self, {{ module_name }}_id: int) -> bool:
        pass
""",

    "use_case": """\
from typing import List, Optional
from src.domain.entities.{{ module_name }} import {{ class_name }}
from src.domain.repositories.{{ module_name }}_repository import {{ class_name }}Repository

class Create{{ class_name }}UseCase:
    def __init__(self, {{ module_name }}_repository: {{ class_name }}Repository):
        self.{{ module_name }}_repository = {{ module_name }}_repository
    
    def execute(self, {{ module_name }}_data: dict) -> {{ class_name }}:
        {{ module_name }} = {{ class_name }}(**{{ module_name }}_data)
        return self.{{ module_name }}_repository.save({{ module_name }})

class Get{{ class_name }}UseCase:
    def __init__(self, {{ module_name }}_repository: {{ class_name }}Repository):
        self.{{ module_name }}_repository = {{ module_name }}_repository
    
    def get_by_id(self, {{ module_name }}_id: int) -> Optional[{{ class_name }}]:
        return self.{{ module_name }}_repository.get_by_id({{ module_name }}_id)
    
    def get_all(self) -> List[{{ class_name }}]:
        return self.{{ module_name }}_repository.get_all()
""",

    "infrastructure_repository": """\
from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.entities.{{ module_name }} import {{ class_name }}
from src.domain.repositories.{{ module_name }}_repository import {{ class_name }}Repository
from src.infrastructure.database.models import SQL{{ class_name }}

class SQLAlchemy{{ class_name }}Repository({{ class_name }}Repository):
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, {{ module_name }}: {{ class_name }}) -> {{ class_name }}:
        db_{{ module_name }} = SQL{{ class_name }}(
            **{{ module_name }}.__dict__
        )
        self.db.add(db_{{ module_name }})
        self.db.commit()
        self.db.refresh(db_{{ module_name }})
        return {{ class_name }}(
            id=db_{{ module_name }}.id,
            created_at=db_{{ module_name }}.created_at,
            updated_at=db_{{ module_name }}.updated_at
        )
    
    def get_by_id(self, {{ module_name }}_id: int) -> Optional[{{ class_name }}]:
        db_{{ module_name }} = self.db.query(SQL{{ class_name }}).filter(
            SQL{{ class_name }}.id == {{ module_name }}_id
        ).first()
        if db_{{ module_name }}:
            return {{ class_name }}(
                id=db_{{ module_name }}.id,
                created_at=db_{{ module_name }}.created_at,
                updated_at=db_{{ module_name }}.updated_at
            )
        return None
    
    def get_all(self) -> List[{{ class_name }}]:
        db_{{ module_name }}s = self.db.query(SQL{{ class_name }}).all()
        return [
            {{ class_name }}(
                id=u.id,
                created_at=u.created_at,
                updated_at=u.updated_at
            ) for u in db_{{ module_name }}s
        ]
    
    def delete(self, {{ module_name }}_id: int) -> bool:
        db_{{ module_name }} = self.db.query(SQL{{ class_name }}).filter(
            SQL{{ class_name }}.id == {{ module_name }}_id
        ).first()
        if db_{{ module_name }}:
            self.db.delete(db_{{ module_name }})
            self.db.commit()
            return True
        return False
""",

    "infrastructure_model": """\
from sqlalchemy import Column, Integer, DateTime
from src.infrastructure.database.database import Base

class SQL{{ class_name }}(Base):
    __tablename__ = "{{ table_name }}"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SQL{{ class_name }}(id={{self.id}})>"
""",

    "interface_schema": """\
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class {{ class_name }}Create(BaseModel):
    pass

class {{ class_name }}Response(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
""",

    "web_app": """\
from fastapi import FastAPI, HTTPException
from src.application.use_cases.create_{{ module_name }} import Create{{ class_name }}UseCase
from src.application.use_cases.get_{{ module_name }} import Get{{ class_name }}UseCase
from src.interface_adapters.schemas.{{ module_name }} import {{ class_name }}Create, {{ class_name }}Response

def create_app(
    create_{{ module_name }}_uc: Create{{ class_name }}UseCase,
    get_{{ module_name }}_uc: Get{{ class_name }}UseCase
) -> FastAPI:
    app = FastAPI(title="{{ project_slug }}", version="1.0.0")
    
    @app.post("/{{ module_name }}s", response_model={{ class_name }}Response)
    def create_{{ module_name }}({{ module_name }}_data: {{ class_name }}Create):
        try:
            {{ module_name }} = create_{{ module_name }}_uc.execute({{ module_name }}_data.dict())
            return {{ class_name }}Response(
                id={{ module_name }}.id,
                created_at={{ module_name }}.created_at,
                updated_at={{ module_name }}.updated_at
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.get("/{{ module_name }}s/{{{ module_name }}_id}", response_model={{ class_name }}Response)
    def get_{{ module_name }}({{ module_name }}_id: int):
        {{ module_name }} = get_{{ module_name }}_uc.get_by_id({{ module_name }}_id)
        if not {{ module_name }}:
            raise HTTPException(status_code=404, detail="{{ class_name }} not found")
        return {{ class_name }}Response(
            id={{ module_name }}.id,
            created_at={{ module_name }}.created_at,
            updated_at={{ module_name }}.updated_at
        )
    
    @app.get("/{{ module_name }}s", response_model=list[{{ class_name }}Response])
    def get_all_{{ module_name }}s():
        {{ module_name }}s = get_{{ module_name }}_uc.get_all()
        return [
            {{ class_name }}Response(
                id={{ module_name }}.id,
                created_at={{ module_name }}.created_at,
                updated_at={{ module_name }}.updated_at
            ) for {{ module_name }} in {{ module_name }}s
        ]
    
    @app.get("/")
    def read_root():
        return {"message": "FastAPI with Clean Architecture"}
    
    return app
""",

    "database_config": """\
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
"""
}
