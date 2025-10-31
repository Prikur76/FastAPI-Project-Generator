"""
Парсер YAML файлов со стандартизированной структурой.
"""

import yaml
from pathlib import Path
from typing import List
from .base import BaseParser
from fastapi_generator.core.models import ProjectFile, ProjectSchema


class YamlParser(BaseParser):
    """Парсит YAML файлы со стандартизированной структурой."""
    
    def parse(self, file_path: Path) -> ProjectSchema:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            raise SystemExit(f"❌ Ошибка чтения YAML: {e}")
        
        if not isinstance(data, dict):
            raise SystemExit("❌ YAML должен содержать словарь.")
        
        # Извлекаем метаданные
        metadata = data.get('metadata', {})
        architecture = metadata.get('architecture', 'layered')
        structure = data.get('structure', {})
        
        # Корневая директория
        root_dir = structure.get('root_dir', '')
        if root_dir and not root_dir.endswith('/'):
            root_dir += '/'
        
        # Обрабатываем файлы
        files_data = structure.get('files', [])
        files = []
        
        for item in files_data:
            if isinstance(item, dict):
                path = item.get('path', '')
                class_name = item.get('class', '')
                file_type = item.get('type', 'default')
                template = item.get('template', 'default')
                
                if path and class_name:
                    # Добавляем корневую директорию если указана
                    if root_dir and not path.startswith(root_dir):
                        full_path = f"{root_dir}{path}"
                    else:
                        full_path = path
                    
                    # Автодетект типа и шаблона если не указаны
                    if file_type == 'default':
                        file_type = self._detect_file_type(full_path, architecture)
                    if template == 'default':
                        template = self._detect_template(full_path, file_type, architecture)
                    
                    files.append(self._create_project_file(
                        full_path, class_name, file_type, template
                    ))
        
        # Добавляем root_dir в метаданные
        if root_dir:
            metadata['root_dir'] = root_dir.rstrip('/')
        
        return self._create_project_schema(architecture, files, metadata)