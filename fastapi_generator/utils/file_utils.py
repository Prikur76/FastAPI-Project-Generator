"""
Утилиты для работы с файлами.
"""

import zipfile
from pathlib import Path


def zip_directory(folder_path: Path, zip_path: Path) -> None:
    """Создает ZIP-архив папки."""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in folder_path.rglob('*'):
            if file.is_file():
                arcname = file.relative_to(folder_path.parent)
                zipf.write(file, arcname)
