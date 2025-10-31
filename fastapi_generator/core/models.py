"""
Модели данных для генератора.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any


@dataclass
class ProjectFile:
    """Модель файла проекта."""
    path: str
    class_name: str
    file_type: str = "default"
    template: str = "default"
    content: str = ""
    
    @property
    def normalized_path(self) -> str:
        """Возвращает путь с нормализованными разделителями."""
        return self.path.replace('\\', '/')
    
    @property
    def module_name(self) -> str:
        return self.class_name.lower()
    
    @property 
    def table_name(self) -> str:
        return f"{self.module_name}s"
    
    @property
    def filename(self) -> str:
        return Path(self.path).name
    

@dataclass
class ProjectSchema:
    """Стандартизированная схема проекта."""
    architecture: str
    files: List[ProjectFile]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def project_name(self) -> str:
        return self.metadata.get('name', 'FastAPI Project')
    
    @property
    def description(self) -> str:
        return self.metadata.get('description', '')
    
    @property
    def root_dir(self) -> str:
        return self.metadata.get('root_dir', '')