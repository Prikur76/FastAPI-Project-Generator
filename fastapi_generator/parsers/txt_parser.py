"""
Парсер TXT файлов с конвертацией в стандартный формат.
"""

import re
from pathlib import Path
from typing import List
from .base import BaseParser
from fastapi_generator.core.models import ProjectFile, ProjectSchema


class TxtParser(BaseParser):
    """Парсит TXT файлы и конвертирует в стандартный формат."""
    
    def parse(self, file_path: Path) -> ProjectSchema:
        print(f"🔍 Парсим TXT файл: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        files = []
        current_path = ""
        root_dir = ""
        
        for line in content.split('\n'):
            line = line.rstrip('\n')
            if not line.strip():
                continue
                
            # Определяем уровень вложенности
            indent_level = self._get_indent_level(line)
            clean_line = self._clean_line(line)
            
            # Пропускаем комментарии без файлов
            if clean_line.startswith('#') and '.py' not in clean_line:
                continue
            
            # Если это корневая директория (уровень 0 и заканчивается на /)
            if indent_level == 0 and clean_line.endswith('/'):
                root_dir = clean_line.rstrip('/')
                current_path = root_dir
                continue
            
            # Если это директория (заканчивается на /)
            if clean_line.endswith('/'):
                dir_name = clean_line.rstrip('/')
                if indent_level == 0:
                    current_path = dir_name
                else:
                    current_path_parts = current_path.split('/') if current_path else []
                    if len(current_path_parts) > indent_level:
                        current_path_parts = current_path_parts[:indent_level]
                    current_path_parts.append(dir_name)
                    current_path = '/'.join(current_path_parts)
                continue
            
            # Если это файл .py
            project_file = self._parse_py_file_line(clean_line, current_path)
            if project_file:
                files.append(project_file)
        
        # Определяем архитектуру по содержимому
        architecture = self._detect_architecture_from_content(content, files)
        
        metadata = {
            'name': 'Generated from TXT',
            'description': 'Автоматически сгенерировано из TXT схемы',
            'architecture': architecture,
            'root_dir': root_dir
        }
        
        print(f"📄 Распознано {len(files)} файлов, архитектура: {architecture}")
        return self._create_project_schema(architecture, files, metadata)
    
    def _get_indent_level(self, line: str) -> int:
        """Определяет уровень вложенности."""
        indent_match = re.match(r'^([├└│─\s]*)', line)
        if indent_match:
            indent_chars = indent_match.group(1)
            normalized_indent = len(indent_chars.replace('├', ' ').replace('└', ' ').replace('│', ' ').replace('─', ' '))
            return normalized_indent // 4
        return 0
    
    def _clean_line(self, line: str) -> str:
        """Очищает строку от символов форматирования."""
        return re.sub(r'^[├└│─\s]*', '', line).strip()
    
    def _parse_py_file_line(self, line: str, current_path: str):
        """Парсит строку с указанием .py файла."""
        # Ищем основной паттерн: filename.py # → ClassName
        pattern = r'([a-zA-Z0-9_.-]+\.py)\s*#\s*→\s*([A-Za-z_]\w*)'
        match = re.search(pattern, line)
        if match:
            filename = match.group(1).strip()
            class_name = match.group(2).strip()
            
            # Формируем полный путь
            if current_path:
                full_path = f"{current_path}/{filename}"
            else:
                full_path = filename
            
            # Автоматически определяем тип и шаблон
            file_type = self._detect_file_type(full_path, 'modular')
            template = self._detect_template(full_path, file_type, 'modular')
            
            return self._create_project_file(full_path, class_name, file_type, template)
        
        return None
    
    def _detect_architecture_from_content(self, content: str, files: List[ProjectFile]) -> str:
        """Определяет архитектуру по содержимому TXT."""
        content_lower = content.lower()
        paths = [f.path for f in files]
        
        # Проверяем пути файлов для определения архитектуры
        if any('domain/entities' in path for path in paths):
            return 'clean'
        elif any('application/use_cases' in path for path in paths):
            return 'clean'
        elif any('services/' in path and 'repositories/' in path for path in paths):
            return 'layered'
        elif any('api/v1/endpoints' in path for path in paths):
            return 'layered'
        else:
            return 'modular'