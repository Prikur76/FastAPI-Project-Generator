"""
Шаблоны для генерации FastAPI проектов.
"""

from .layered import LAYERED_TEMPLATES
from .clean import CLEAN_TEMPLATES
from .modular import MODULAR_TEMPLATES

# Объединяем все шаблоны
TEMPLATES = {
    "layered": LAYERED_TEMPLATES,
    "clean": CLEAN_TEMPLATES,
    "modular": MODULAR_TEMPLATES
}

__all__ = ['TEMPLATES', 'LAYERED_TEMPLATES', 'CLEAN_TEMPLATES', 'MODULAR_TEMPLATES']