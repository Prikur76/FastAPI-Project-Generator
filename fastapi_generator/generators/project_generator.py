"""
Фасад для генерации всего проекта.
"""

from pathlib import Path
"""
Фасад для генерации всего проекта.
"""

from pathlib import Path
from typing import List, Union, Tuple
from .file_generator import FileGenerator
from .config_generator import ConfigGenerator
from .test_generator import TestGenerator
from ..core.models import ProjectFile


class ProjectGenerator:
    """Фасад для генерации всего проекта."""
    
    def __init__(self, architecture: str, templates: dict):
        self.architecture = architecture
        self.file_generator = FileGenerator(architecture, templates)
        self.config_generator = ConfigGenerator(architecture)
        # self.test_generator = TestGenerator(architecture)
    
    def create_structure(self, files, project_root: Path, with_init: bool = True) -> None:
        """Создает всю структуру проекта."""
        # Конвертируем входные данные в ProjectFile объекты
        project_files = self._convert_to_project_files(files)
        
        self._create_directories(project_files, project_root)
        
        if with_init:
            self._create_init_files(project_files, project_root)
        
        self.file_generator.generate(project_root, project_files)
        self.config_generator.generate(project_root, project_files)
        # self.test_generator.generate(project_root, project_files)
    
    def _convert_to_project_files(self, files) -> List[ProjectFile]:
        """Конвертирует входные данные в список ProjectFile."""
        project_files = []
        for item in files:
            if isinstance(item, ProjectFile):
                # Уже объект ProjectFile
                project_files.append(item)
            elif isinstance(item, tuple) and len(item) == 2:
                # Это кортеж (file_path, class_name)
                file_path, class_name = item
                project_files.append(ProjectFile(path=file_path, class_name=class_name))
            else:
                raise ValueError(f"Неизвестный формат данных: {type(item)} - {item}")
        return project_files
    
    def _create_directories(self, files: List[ProjectFile], project_root: Path) -> None:
        """Создает все необходимые директории."""
        directories = set()
        
        for project_file in files:
            full_path = project_root / project_file.path
            directories.add(full_path.parent)
        
        for directory in sorted(directories):
            directory.mkdir(parents=True, exist_ok=True)
    
    def _create_init_files(self, files: List[ProjectFile], project_root: Path) -> None:
        """Создает __init__.py файлы."""
        directories = set()
        
        for project_file in files:
            full_path = project_root / project_file.path
            directory = full_path.parent
            if directory != project_root:
                directories.add(directory)
        
        for directory in sorted(directories):
            init_file = directory / '__init__.py'
            if not init_file.exists():
                init_file.write_text(f"# {directory.relative_to(project_root)}/__init__.py\n")