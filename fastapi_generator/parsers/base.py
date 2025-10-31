"""
Базовый класс для парсеров схем.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List
from fastapi_generator.core.models import ProjectFile, ProjectSchema


class BaseParser(ABC):
    """Абстрактный базовый класс парсера."""
    
    @abstractmethod
    def parse(self, file_path: Path) -> ProjectSchema:
        """Парсит файл и возвращает стандартизированную схему."""
        pass
    
    def _normalize_path(self, path: str) -> str:
        """Нормализует путь, заменяя обратные слеши на прямые."""
        return path.replace('\\', '/')

    def _create_project_file(self, path: str, class_name: str, 
                             file_type: str = "default", template: str = "default") -> ProjectFile:
        """Создает объект ProjectFile."""
        normalized_path = self._normalize_path(path)        
        return ProjectFile(
            path=normalized_path, 
            class_name=class_name,
            file_type=file_type,
            template=template
        )
    
    def _create_project_schema(self, architecture: str, files: List[ProjectFile], 
                               metadata: Dict[str, Any] | None = None) -> ProjectSchema:
        """Создает стандартизированную схему проекта."""
        if metadata is None:
            metadata = {}
        
        return ProjectSchema(
            architecture=architecture,
            files=files,
            metadata=metadata
        )
    
    def _detect_file_type(self, path: str, architecture: str) -> str:
        """Определяет тип файла по пути."""
        path_lower = path.lower()
        
        if path.endswith('__init__.py'):
            return 'package'
        elif 'main.py' in path:
            return 'main'
        elif 'config.py' in path or 'settings.py' in path:
            return 'config'
        elif 'database.py' in path or 'db.py' in path:
            return 'database'
        elif 'model' in path_lower or 'entity' in path_lower:
            return 'model'
        elif 'schema' in path_lower or 'dto' in path_lower:
            return 'schema'
        elif 'service' in path_lower or 'use_case' in path_lower:
            return 'service'
        elif 'repository' in path_lower:
            return 'repository'
        elif 'router' in path_lower or 'endpoint' in path_lower:
            return 'router'
        elif 'crud' in path_lower:
            return 'crud'
        elif 'test' in path_lower:
            return 'test'
        elif 'util' in path_lower or 'helper' in path_lower:
            return 'util'
        
        return 'default'
    
    def _detect_template(self, path: str, file_type: str, architecture: str) -> str:
        """Определяет шаблон для файла."""
        # Для разных архитектур могут быть разные шаблоны
        if architecture == "clean":
            if file_type == "model":
                return "domain_entity"
            elif file_type == "repository":
                return "domain_repository"
            elif file_type == "service":
                return "use_case"
        
        return file_type