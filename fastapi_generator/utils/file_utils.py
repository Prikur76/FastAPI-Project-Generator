"""
Утилиты для работы с файлами.
"""

import zipfile
from pathlib import Path


def ensure_output_dir() -> Path:
    """Создает и возвращает путь к директории output."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    return output_dir


def get_output_path(filename: str, output_dir: Path | None = None) -> Path:
    """Возвращает полный путь в директории output."""
    if output_dir is None:
        output_dir = ensure_output_dir()
    return output_dir / filename


def zip_directory(folder_path: Path, zip_path: Path | None = None) -> Path:
    """Создает ZIP-архив папки в директории output."""
    if zip_path is None:
        zip_name = f"{folder_path.name}.zip"
        zip_path = get_output_path(zip_name)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in folder_path.rglob('*'):
            if file.is_file():
                arcname = file.relative_to(folder_path.parent)
                zipf.write(file, arcname)
    
    return zip_path
