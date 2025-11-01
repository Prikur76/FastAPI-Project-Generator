"""
Генератор тестовых файлов.
"""

from pathlib import Path
from typing import List
from .base import BaseGenerator
from ..core.models import ProjectFile


class TestGenerator(BaseGenerator):
    """Генерирует тестовые файлы."""
    
    def generate(self, project_root: Path, files) -> None:
        """Генерирует тесты для файлов проекта (реализация абстрактного метода)."""
        self.generate_tests(project_root, files)
    
    def generate_tests(self, project_root: Path, files) -> None:
        """Генерирует тесты для файлов проекта."""
        project_files = self._convert_to_project_files(files)
        
        # Фильтруем файлы для которых нужно генерировать тесты
        files_to_test = self._filter_files_for_testing(project_files)
        
        print(f"🧪 Генерация тестов для {len(files_to_test)} файлов")
        
        # Используем set для отслеживания уже созданных тестов
        created_tests = set()
        
        for project_file in files_to_test:
            test_path = self._get_test_path(project_root, project_file)
            
            # Проверяем, не создавали ли мы уже тест для этого пути
            if test_path.as_posix() in created_tests:
                continue
                
            # Проверяем, не существует ли уже тест
            if test_path.exists():
                print(f"⚠️  Тест уже существует: {test_path}")
                continue
            
            self._ensure_directory(test_path.parent)
            
            content = self._generate_test_content(project_file, test_path)
            test_path.write_text(content, encoding='utf-8')
            print(f"✅ Создан тест: {test_path}")
            created_tests.add(test_path.as_posix())
    
    def _filter_files_for_testing(self, project_files: List[ProjectFile]) -> List[ProjectFile]:
        """Фильтрует файлы для которых нужно генерировать тесты."""
        filtered_files = []
        processed_paths = set()  # Для отслеживания уже обработанных путей
        
        for project_file in project_files:
            # Пропускаем __init__.py файлы
            if project_file.path.endswith('__init__.py'):
                continue
            
            # Пропускаем файлы которые уже находятся в tests/ директории
            if 'tests/' in project_file.path.lower() or 'test_' in Path(project_file.path).name:
                continue
            
            # Пропускаем конфигурационные и служебные файлы
            if self._is_config_file(project_file.path):
                continue
            
            # Пропускаем если уже обрабатывали этот путь (избегаем дублирования)
            if project_file.path in processed_paths:
                continue
            
            filtered_files.append(project_file)
            processed_paths.add(project_file.path)
        
        return filtered_files
    
    def _is_config_file(self, file_path: str) -> bool:
        """Определяет является ли файл конфигурационным."""
        config_files = {
            'config.py', 'settings.py', 'database.py', 'main.py',
            'conftest.py', 'env.py', 'alembic.ini', 'pyproject.toml'
        }
        
        filename = Path(file_path).name
        return filename in config_files
    
    def _generate_test_file(self, project_root: Path, project_file: ProjectFile):
        """Генерирует тестовый файл для одного файла проекта."""
        # Определяем путь для теста
        test_path = self._get_test_path(project_root, project_file)
        
        # Проверяем, не существует ли уже тест
        if test_path.exists():
            print(f"⚠️  Тест уже существует: {test_path}")
            return
        
        self._ensure_directory(test_path.parent)
        
        content = self._generate_test_content(project_file, test_path)
        test_path.write_text(content, encoding='utf-8')
        print(f"✅ Создан тест: {test_path}")
    
    def _get_test_path(self, project_root: Path, project_file: ProjectFile) -> Path:
        """Определяет путь для тестового файла."""
        source_path = Path(project_file.path)
        
        # Создаем соответствующую структуру в tests/ директории
        if self.architecture == "clean":
            # Для clean architecture: tests/src/... (убираем лишний src)
            if source_path.parts[0] == 'src':
                # Если путь начинается с src/, убираем его для тестов
                relative_path = Path(*source_path.parts[1:])
            else:
                relative_path = source_path
            test_dir = project_root / "tests" / "src"
        else:
            # Для layered и modular: tests/...
            test_dir = project_root / "tests"
            relative_path = source_path
        
        # Сохраняем структуру исходных файлов
        test_path = test_dir / relative_path.parent / f"test_{relative_path.name}"
        
        return test_path
    
    def _generate_test_content(self, project_file: ProjectFile, test_path: Path) -> str:
        """Генерирует содержимое тестового файла."""
        class_name = project_file.class_name
        module_name = project_file.module_name
        
        # Нормализуем путь для отображения
        normalized_test_path = test_path.as_posix()  # Используем as_posix() для нормализации
        
        # Определяем импорты в зависимости от архитектуры
        imports = self._generate_imports(project_file)
        
        # Проверяем, является ли импорт закомментированным (проблемный случай)
        if imports.startswith('#') or 'might need adjustment' in imports:
            content = f'''# {normalized_test_path}

{imports}
import pytest


# NOTE: Test for {class_name} - import might need manual adjustment
def test_{module_name}_basic():
    """Базовый тест для {class_name}."""
    assert True

def test_{module_name}_functionality():
    """Тест функциональности {class_name}."""
    assert True
'''
        else:
            content = f'''# {test_path}

{imports}
import pytest


class Test{class_name}:
    """Тесты для {class_name}."""
    
    def test_{module_name}_creation(self):
        """Тест создания {class_name}."""
        assert True
    
    def test_{module_name}_methods(self):
        """Тест методов {class_name}."""
        assert True


def test_{module_name}_function():
    """Тест функции для {class_name}."""
    assert True
'''
        return content
    
    def _generate_imports(self, project_file: ProjectFile) -> str:
        """Генерирует импорты для тестового файла."""
        source_path = Path(project_file.path)
        
        # Для clean architecture убираем начальный src/ если есть
        if self.architecture == "clean" and source_path.parts[0] == 'src':
            import_path = '.'.join(source_path.with_suffix('').parts[1:])
        else:
            import_path = source_path.with_suffix('').as_posix().replace('/', '.')
        
        # Пытаемся создать корректный импорт
        try:
            return f"from {import_path} import {project_file.class_name}"
        except Exception as e:
            print(f"⚠️  Ошибка создания импорта для {project_file.path}: {e}")
            return f"# from {import_path} import {project_file.class_name}"
    
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