"""
Базовый класс для генераторов.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from ..core.models import ProjectFile


class BaseGenerator(ABC):
    """Абстрактный базовый класс генератора."""
    
    def __init__(self, architecture: str):
        self.architecture = architecture
    
    @abstractmethod
    def generate(self, project_root: Path, files: List[ProjectFile]) -> None:
        """Генерирует часть проекта."""
        pass
    
    def _ensure_directory(self, path: Path) -> None:
        """Создает директорию если не существует."""
        path.mkdir(parents=True, exist_ok=True)
