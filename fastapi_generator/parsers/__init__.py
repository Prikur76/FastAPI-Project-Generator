from .base import BaseParser
from .txt_parser import TxtParser
from .json_parser import JsonParser
from .yaml_parser import YamlParser


class SchemaParser:
    """Фасад для парсеров разных форматов."""
    
    def __init__(self):
        self._parsers = {
            '.txt': TxtParser(),
            '.json': JsonParser(), 
            '.yaml': YamlParser(),
            '.yml': YamlParser()
        }
    
    def parse_file(self, file_path) -> 'ProjectSchema':
        """Парсит файл схемы и возвращает стандартизированную схему."""
        if not file_path.exists():
            raise SystemExit(f"❌ Файл не найден: {file_path}")
        
        parser = self._parsers.get(file_path.suffix)
        if not parser:
            raise SystemExit("❌ Поддерживаются только: .txt, .json, .yaml, .yml")
        
        return parser.parse(file_path)


__all__ = ['SchemaParser', 'TxtParser', 'JsonParser', 'YamlParser']