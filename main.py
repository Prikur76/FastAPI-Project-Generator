#!/usr/bin/env python3
"""
Генератор FastAPI-проектов по схеме с поддержкой uv и различных архитектур.
"""

import argparse
import shutil
from pathlib import Path

from fastapi_generator.core.config import TEMPLATES
from fastapi_generator.parsers import SchemaParser
from fastapi_generator.generators import ProjectGenerator, ConfigGenerator, TestGenerator
from fastapi_generator.utils.file_utils import zip_directory


def main():
    parser = argparse.ArgumentParser(
        description="Генератор FastAPI-проектов по схеме с поддержкой uv и различных архитектур.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument('-i', '--input', type=str, required=True,
                        help='Файл со схемой: .txt, .json, .yaml, .yml')
    parser.add_argument('-o', '--output', type=str, default='fastapi_project',
                        help='Имя выходного проекта')
    parser.add_argument('--no-init', action='store_true', help='Не создавать __init__.py')
    parser.add_argument('--zip', action='store_true', help='Создать ZIP-архив проекта')
    parser.add_argument('--zip-only', action='store_true',
                        help='Удалить папку после создания ZIP-архива')
    parser.add_argument('--with-tests', action='store_true',
                        help='Генерировать тесты для файлов проекта')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_name = args.output
    project_root = Path(output_name).resolve()
    
    # Парсим схему
    parser = SchemaParser()
    project_schema = parser.parse_file(input_path)
    
    architecture = project_schema.architecture
    file_data = project_schema.files
    
    print(f"🔍 Результат парсинга:")
    print(f"   Архитектура: {architecture}")
    print(f"   Файлов: {len(file_data)}")
    print(f"   Проект: {project_schema.project_name}")
    if project_schema.description:
        print(f"   Описание: {project_schema.description}")
    
    for i, project_file in enumerate(file_data[:10]):
        print(f"   {i}: {project_file.normalized_path} -> {project_file.class_name}")
    if len(file_data) > 10:
        print(f"   ... и еще {len(file_data) - 10} файлов")
    
    if not file_data:
        raise SystemExit("❌ Не распознано ни одного .py-файла.")
    
    print(f"🏗️  Создание FastAPI проекта: {project_schema.project_name}")
    print(f"📋 Архитектура: {architecture}")
    
    # Удаляем существующую папку
    if project_root.exists():
        shutil.rmtree(project_root)
    
    # Генерируем проект
    project_gen = ProjectGenerator(architecture, TEMPLATES)
    project_gen.create_structure(file_data, project_root, with_init=not args.no_init)
    
    config_gen = ConfigGenerator(architecture)
    config_gen.generate(project_root, file_data)
    
    # Генерируем тесты только если указан флаг 
    if args.with_tests:
        test_gen = TestGenerator(architecture)
        test_gen.generate(project_root, file_data)
    
    # Создаём ZIP если нужно
    if args.zip or args.zip_only:
        zip_filename = Path(f"{output_name}.zip")
        print(f"📦 Упаковка в архив: {zip_filename}")
        zip_directory(project_root, zip_filename)
        
        if args.zip_only:
            print(f"🗑️  Удаление временной папки: {project_root}")
            shutil.rmtree(project_root)
    
    # Статистика
    _print_statistics(file_data, architecture, project_root, args)
    
    print(f"\n🚀 Для начала работы:")
    print(f"   cd {output_name}")
    print(f"   uv sync")
    print(f"   uv run dev")


def _print_statistics(file_data, architecture, project_root, args):
    """Выводит статистику проекта."""
    # Используем объекты ProjectFile
    entities = sum(1 for project_file in file_data 
                  if 'entities' in project_file.normalized_path or 'models' in project_file.normalized_path)
    services = sum(1 for project_file in file_data 
                  if 'services' in project_file.normalized_path or 'use_cases' in project_file.normalized_path)
    routers = sum(1 for project_file in file_data 
                 if 'routers' in project_file.normalized_path or 'endpoints' in project_file.normalized_path)
    total_files = len(file_data)
    
    print(f"📊 Статистика:")
    print(f"   🏗️  Архитектура: {architecture}")
    print(f"   📦 Модели/Сущности: {entities}")
    print(f"   ⚙️  Сервисы/Use Cases: {services}")
    print(f"   🌐 Роутеры: {routers}")
    print(f"   📁 Всего файлов: {total_files}")
    
    if args.zip or args.zip_only:
        print(f"📦 ZIP-архив: {project_root}.zip")


if __name__ == '__main__':
    main()