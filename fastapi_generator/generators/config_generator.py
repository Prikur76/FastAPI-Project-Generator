"""
Генератор конфигурационных файлов проекта.
"""

from pathlib import Path
from typing import List
from .base import BaseGenerator
from ..core.models import ProjectFile
from ..core.config import ARCHITECTURE_STRUCTURES


class ConfigGenerator(BaseGenerator):
    """Генерирует конфигурационные файлы проекта."""
    
    def generate(self, project_root: Path, files: List[ProjectFile]) -> None:
        """Генерирует все конфигурационные файлы."""
        self._generate_pyproject_toml(project_root)
        self._generate_readme(project_root)
        self._generate_gitignore(project_root)
        self._generate_ruff_toml(project_root)
        self._generate_editorconfig(project_root)
        self._generate_main_file(project_root)
    
    def _generate_pyproject_toml(self, project_root: Path) -> None:
        """Генерирует pyproject.toml для uv."""
        project_slug = project_root.name.lower().replace(' ', '_').replace('-', '_')
        
        content = f'''[project]
name = "{project_slug}"
version = "0.1.0"
description = "FastAPI project with {self.architecture} architecture"
readme = "README.md"
requires-python = ">=3.12.*"
dependencies = [
    "fastapi[standard]>=0.110.0",
    "uvicorn>=0.27.0",
    "sqlalchemy>=2.0.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "ruff==0.14.2",
]

'''
        (project_root / "pyproject.toml").write_text(content, encoding='utf-8')
    
    def _generate_readme(self, project_root: Path) -> None:
        """Генерирует README.md."""
        structure = ARCHITECTURE_STRUCTURES.get(self.architecture, "")
        
        content = f'''# {project_root.name}

FastAPI project with {self.architecture} architecture.

## 🚀 Quick Start

```bash
uv sync
uv run dev
```

## 📁 Architecture

```
{structure}
```
'''
        (project_root / "README.md").write_text(content, encoding='utf-8')

    def _generate_ruff_toml(self, project_root: Path) -> None:
        """Генерирует ruff.toml."""
        content = '''# Exclude a variety of commonly ignored directories.
exclude = [
    ".bzr",
    ".direnv",
    ".eggs",
    ".git",
    ".git-rewrite",
    ".hg",
    ".ipynb_checkpoints",
    ".mypy_cache",
    ".nox",
    ".pants.d",
    ".pyenv",
    ".pytest_cache",
    ".pytype",
    ".ruff_cache",
    ".svn",
    ".tox",
    ".venv",
    ".vscode",
    "__pypackages__",
    "_build",
    "buck-out",
    "build",
    "dist",
    "node_modules",
    "site-packages",
    "venv",
    "env",
    "migrations",
]

line-length = 120

# Assume Python 3.9
target-version = "py39"

[lint.mccabe]
max-complexity = 7

[lint.pylint]
max-args = 6 # Максимальное кол-во аргументов функции
max-branches = 10 # Максимальное кол-во ветвей if/else
max-statements = 50 # Максимальное кол-во операторов в функции

[lint.per-file-ignores]
"**/__init__.py" = ["F401"]
"**/test*.py" = ["PLR2004", "PLR0913", "PLR0915", "C901"]
"**/template_html.py" = ["E501"]

[lint.isort]
known-first-party = []
force-single-line = false
relative-imports-order = "closest-to-furthest"
combine-as-imports = true

[lint]
preview = true # Enables experimental rules like E225
select = [
    "A", # flake8-builtins (переопределение встроенных имен)
    "B", # flake8-bugbear -- опасные паттерны (использование x == None вместо x is None, и т.д.)
    "C", # flake8-comprehensions (ненужный list(), ненужный dict())
    "E", # Ошибки из pycodestyle (PEP 8)
    "F", # Логические ошибки и потенциальные баги (неиспользуемый импорт, обращение к необъявленной переменной, и т.д.)
    "I", # isort (сортировка импортов)
    "W", # Предупреждения из pycodestyle (пробелы в конце строки, пустые строки, и т.д.)
    "UP", # pyupgrade -- модернизация кода (замена type(x) == int на isinstance(x, int), и т.д.)
    "PL", # Pylint правила (сложность функции, глобальные переменные)
    "RET", # проверка return-ов
    "COM", # Запятые
]
fixable = [
    "E",
    "F401",
    "I",
    "W",
    "COM",
]
unfixable = [
    "A",
    "B",
    "C",
    "PL",
    "RET",
    "UP",
]
ignore = [
    "RET501", # запрет на `return None` -- конфликт с mypy
    "RET504", # лишнее определение переменной перед return
    "B904", # Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None`
    "UP031", # Use format specifiers instead of percent format
    "PLR6301", # Method could be a function, class method, or static method
    "PLC0415", # `import` should be at the top-level of a file
    "B008", # Do not perform function call in argument defaults
    "COM812" # Checks for the absence of trailing commas
]

# Allow unused variables when underscore-prefixed.
dummy-variable-rgx = "^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$"
'''
        (project_root / "ruff.toml").write_text(content, encoding='utf-8')
    
    def _generate_main_file(self, project_root: Path) -> None:
        """Генерирует основной файл приложения."""
        project_slug = project_root.name.lower().replace(' ', '_').replace('-', '_')
        
        if self.architecture == "layered":
            content = f'''from fastapi import FastAPI

app = FastAPI(title="{project_slug}")

@app.get("/")
def read_root():
    return {{"message": "FastAPI with {self.architecture} architecture"}}
'''
            main_path = project_root / "app" / "main.py"
        elif self.architecture == "clean":
            content = f'''from fastapi import FastAPI

app = FastAPI(title="{project_slug}")

@app.get("/")
def read_root():
    return {{"message": "FastAPI with {self.architecture} architecture"}}
'''
            main_path = project_root / "src" / "main.py"
        else:  # modular
            # Для modular архитектуры НЕ создаем main.py в корне, 
            # так как он должен быть внутри blog_api/app/main.py
            print("ℹ️  Для modular архитектуры main.py создается через схему")
            return
    
        self._ensure_directory(main_path.parent)
        if not main_path.exists():  # Создаем только если не существует
            main_path.write_text(content, encoding='utf-8')
        
    def _generate_gitignore(self, project_root: Path) -> None:
        """Генерирует .gitignore файл для Python/FastAPI проекта."""
        gitignore_content = '''# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# PEP 582; used by e.g. github.com/David-OConnor/pyflow
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Editor directories and files
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Database files
*.db
*.sqlite
*.sqlite3

# FastAPI specific
*.log
uploads/
temp/

# UV specific
.uv/
    '''
        gitignore_path = project_root / ".gitignore"
        gitignore_path.write_text(gitignore_content, encoding='utf-8')
        
        
    def _generate_editorconfig(self, project_root: Path) -> None:
        """Генерирует .editorconfig файл для Python/FastAPI проекта."""
        editorconfig_content = '''# EditorConfig is awesome: https://editorconfig.org

# top-most EditorConfig file
root = true

[*]
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
charset = utf-8
indent_style = space

[*.{js,html,css,scss}]
indent_size = 2

[*.py]
indent_size = 4

[{Makefile,**.mk}]
# Use tabs for indentation (Makefiles require tabs)
indent_style = tab
'''
        editorconfig_path = project_root / ".editorconfig"
        editorconfig_path.write_text(editorconfig_content, encoding='utf-8')