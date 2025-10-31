"""
Парсер JSON файлов с конвертацией в стандартный формат.
"""

import json
from pathlib import Path
from .base import BaseParser
from fastapi_generator.core.models import ProjectFile, ProjectSchema


class JsonParser(BaseParser):
    """Парсит JSON файлы и конвертирует в стандартный формат."""
    
    def parse(self, file_path: Path) -> ProjectSchema:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            raise SystemExit(f"❌ Ошибка чтения JSON: {e}")
        
        # Определяем архитектуру
        architecture = data.get('architecture', 'layered')
        
        # Обрабатываем файлы в старом и новом формате
        files_data = data.get('files', [])
        files = []
        
        for item in files_data:
            if isinstance(item, dict):
                # Поддержка старого формата (file/class) и нового (path/class)
                path = item.get('path') or item.get('file', '')
                class_name = item.get('class', '')
                
                if path and class_name:
                    # Автоматически определяем тип и шаблон файла
                    file_type = self._detect_file_type(path, architecture)
                    template = self._detect_template(path, file_type, architecture)
                    
                    files.append(self._create_project_file(
                        path, class_name, file_type, template
                    ))
        
        # Создаем метаданные из старого формата
        metadata = {
            'name': data.get('project_name', 'FastAPI Project'),
            'description': data.get('description', ''),
            'architecture': architecture
        }
        
        return self._create_project_schema(architecture, files, metadata)