"""
Генератор файлов проекта на основе шаблонов.
"""

from pathlib import Path
from typing import List, Dict
from .base import BaseGenerator
from ..core.models import ProjectFile


class FileGenerator(BaseGenerator):
    """Генерирует файлы проекта на основе шаблонов."""
    
    def __init__(self, architecture: str, templates: Dict):
        super().__init__(architecture)
        self.templates = templates.get(architecture, {})
    
    def generate(self, project_root: Path, files) -> None:
        """Генерирует все файлы проекта."""
        project_files = self._convert_to_project_files(files)
        for project_file in project_files:
            self._generate_file(project_root, project_file)

    def _convert_to_project_files(self, files) -> List[ProjectFile]:
        """Конвертирует входные данные в список ProjectFile."""
        project_files = []
        for item in files:
            if isinstance(item, ProjectFile):
                project_files.append(item)
            elif isinstance(item, tuple) and len(item) == 2:
                file_path, class_name = item
                project_files.append(ProjectFile(path=file_path, class_name=class_name))
            else:
                raise ValueError(f"Неизвестный формат данных: {type(item)}")
        return project_files
    
    def _generate_file(self, project_root: Path, project_file: ProjectFile) -> None:
        """Генерирует один файл."""
        full_path = project_root / project_file.normalized_path
        self._ensure_directory(full_path.parent)
        
        content = self._generate_content(project_file)
        full_path.write_text(content, encoding='utf-8')
    
    def _generate_content(self, project_file: ProjectFile) -> str:
        """Генерирует содержимое файла."""
        file_type = self._determine_file_type(project_file.normalized_path)
        template = self.templates.get(file_type, self._get_fallback_template())
       
        return template.replace('{{ class_name }}', project_file.class_name)\
                      .replace('{{ module_name }}', project_file.module_name)\
                      .replace('{{ table_name }}', project_file.table_name)\
                      .replace('{{ file_path }}', project_file.normalized_path)
    
    def _determine_file_type(self, file_path: str) -> str:
        """Определяет тип файла на основе пути."""
        parts = Path(file_path).parts
        
        if 'models' in parts or 'entities' in parts:
            return 'model' if self.architecture == 'layered' else 'domain_entity'
        elif 'schemas' in parts:
            return 'schema'
        elif 'services' in parts:
            return 'service'
        elif 'repositories' in parts:
            return 'repository' if self.architecture == 'layered' else 'domain_repository'
        elif 'routers' in parts or 'endpoints' in parts:
            return 'router'
        elif 'use_cases' in parts:
            return 'use_case'
        
        return 'model'  # fallback
    
    def _get_fallback_template(self) -> str:
        """Возвращает шаблон по умолчанию."""
        return f'''# {{{{ file_path }}}}

class {{{{ class_name }}}}:
    """{{{{ class_name }}}} class."""
    
    def __init__(self):
        pass
'''
