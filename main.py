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
from fastapi_generator.utils.file_utils import zip_directory, ensure_output_dir, get_output_path


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
    parser.add_argument('--zip', action='store_true', help='Создать ZIP-архив проекта в output/')
    parser.add_argument('--zip-only', action='store_true',
                        help='Создать только ZIP-архив в output/ (удалить временную папку)')
    parser.add_argument('--with-tests', action='store_true',
                        help='Генерировать тесты для файлов проекта')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_name = args.output
    
    # Создаем output директорию
    output_dir = ensure_output_dir()
    print(f"📁 Выходная директория: {output_dir.resolve()}")
    
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
    
    # Создаем временную папку проекта в текущей директории
    temp_project_root = Path(output_name).resolve()
    
    # Удаляем существующую временную папку
    if temp_project_root.exists():
        shutil.rmtree(temp_project_root)
    
    # Генерируем проект во временной папке
    project_gen = ProjectGenerator(architecture, TEMPLATES)
    project_gen.create_structure(file_data, temp_project_root, with_init=not args.no_init)
    
    config_gen = ConfigGenerator(architecture)
    config_gen.generate(temp_project_root, file_data)
    
    # Генерируем тесты только если указан флаг 
    if args.with_tests:
        test_gen = TestGenerator(architecture)
        test_gen.generate(temp_project_root, file_data)
    
    # Обработка выходных результатов
    final_project_path = None
    zip_file_path = None
    
    if args.zip or args.zip_only:
        # Создаем ZIP в output директории
        zip_filename = f"{output_name}.zip"
        zip_file_path = get_output_path(zip_filename)
        print(f"📦 Упаковка в архив: {zip_file_path}")
        zip_directory(temp_project_root, zip_file_path)
    
    if args.zip_only:
        # Удаляем временную папку, оставляем только ZIP
        print(f"🗑️  Удаление временной папки: {temp_project_root}")
        shutil.rmtree(temp_project_root)
        final_project_path = zip_file_path
    else:
        # Переносим папку проекта в output или оставляем на месте
        if args.zip:
            # Если создавали ZIP, но не только ZIP - оставляем и папку и ZIP
            final_project_dir = get_output_path(output_name)
            if final_project_dir.exists():
                shutil.rmtree(final_project_dir)
            shutil.move(str(temp_project_root), str(final_project_dir))
            final_project_path = final_project_dir
            print(f"📁 Проект перемещен в: {final_project_path}")
        else:
            # Без ZIP - оставляем папку в текущей директории
            final_project_path = temp_project_root
    
    # Статистика
    _print_statistics(file_data, architecture, final_project_path, args, zip_file_path)
    
    print(f"\n🚀 Для начала работы:")
    if not args.zip_only:
        print(f"   cd {final_project_path}")
        print(f"   uv sync")
        print(f"   uv run dev")
    else:
        print(f"   📦 Архив готов: {zip_file_path}")


def _print_statistics(file_data, architecture, project_path, args, zip_path=None):
    """Выводит статистику проекта."""
    entities = sum(1 for project_file in file_data 
                  if 'entities' in project_file.path or 'models' in project_file.path)
    services = sum(1 for project_file in file_data 
                  if 'services' in project_file.path or 'use_cases' in project_file.path)
    routers = sum(1 for project_file in file_data 
                 if 'routers' in project_file.path or 'endpoints' in project_file.path)
    total_files = len(file_data)
    
    print(f"📊 Статистика:")
    print(f"   🏗️  Архитектура: {architecture}")
    print(f"   📦 Модели/Сущности: {entities}")
    print(f"   ⚙️  Сервисы/Use Cases: {services}")
    print(f"   🌐 Роутеры: {routers}")
    print(f"   📁 Всего файлов: {total_files}")
    
    if project_path:
        if args.zip_only:
            print(f"✅ Создан архив: {project_path}")
        else:
            print(f"✅ Создан проект: {project_path}")
    
    if zip_path and not args.zip_only:
        print(f"📦 Дополнительный архив: {zip_path}")


if __name__ == '__main__':
    main()
