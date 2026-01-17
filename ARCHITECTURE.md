# O! My Models - Архитектура проекта

## Обзор

**O! My Models (omymodels)** - универсальная Python библиотека для:
- Генерации ORM-моделей из SQL DDL (CREATE TABLE)
- Конвертации моделей между разными фреймворками (Pydantic → SQLAlchemy и т.д.)

**Версия:** 0.17.0
**Python:** >=3.7
**Лицензия:** MIT

## Структура проекта

```
omymodels/
├── __init__.py              # Публичный API: create_models(), convert_models()
├── from_ddl.py              # Основной модуль генерации из DDL
├── converter.py             # Конвертер между типами моделей
├── cli.py                   # Командная строка (omm)
├── generators.py            # Маршрутизация к генераторам
├── helpers.py               # Утилиты (pluralize, snake_case, etc.)
├── logic.py                 # Логика генерации колонок и таблиц
├── errors.py                # Исключения
├── types.py                 # Базовые определения SQL типов
│
└── models/                  # Генераторы для каждого типа моделей
    ├── gino/                # GinoORM (async PostgreSQL)
    ├── pydantic/            # Pydantic (валидация)
    ├── sqlalchemy/          # SQLAlchemy ORM
    ├── sqlalchemy_core/     # SQLAlchemy Core (Table API)
    ├── sqlmodel/            # SQLModel (SQLAlchemy + Pydantic)
    ├── dataclass/           # Python Dataclasses
    ├── enum/                # Python Enum
    ├── pydal/               # PyDAL (в разработке)
    └── tortoise/            # Tortoise ORM (в разработке)
```

Каждый генератор содержит:
- `core.py` - класс ModelGenerator
- `types.py` - маппинг SQL → целевые типы
- `templates.py` - строковые шаблоны кода
- `*.jinja2` - финальный шаблон файла

## Архитектура

### Поток данных

```
SQL DDL (Input)
     │
     ▼
┌─────────────────────────────┐
│  DDL Parser                 │
│  (simple-ddl-parser)        │
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│  Normalization              │
│  - prepare_data()           │
│  - convert_ddl_to_models()  │
│  - TableMeta объекты        │
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│  Type Conversion            │
│  - types.py маппинг         │
│  - prepare_column_type()    │
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│  Model Generator            │
│  - gino / pydantic / etc.   │
│  - generate_model()         │
│  - create_header()          │
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│  Jinja2 Rendering           │
│  - render_jinja2_template() │
└─────────────────────────────┘
     │
     ▼
Python Code (Output)
```

### Ключевые компоненты

#### 1. ModelGenerator (models/*/core.py)

Базовая структура генератора:

```python
class ModelGenerator:
    def __init__(self):
        self.types_mapping      # SQL → целевой тип
        self.templates          # Шаблоны кода
        self.state              # Отслеживание импортов
        self.custom_types       # Enum и кастомные типы

    def generate_model(table)   # Генерация одной модели
    def create_header(tables)   # Заголовок с импортами
```

#### 2. Система типов (types.py)

Группы SQL типов:
- `string_types`: VARCHAR, CHAR, TEXT, STRING
- `integer_types`: INTEGER, INT, SERIAL, BIGINT, SMALLINT
- `datetime_types`: DATE, TIMESTAMP, DATETIME, TIME
- `bool_types`: BOOLEAN, BOOL
- `float_types`: FLOAT, DECIMAL, NUMERIC, DOUBLE
- `json_types`: JSON, JSONB

#### 3. Логика генерации (logic.py)

- `generate_column()` - полное определение колонки
- `setup_column_attributes()` - nullable, defaults, primary_key
- `add_table_args()` - индексы, constraints, schema
- `add_reference_to_the_column()` - внешние ключи

#### 4. Маршрутизатор (generators.py)

```python
models = {
    "gino": gino.ModelGenerator(),
    "pydantic": pydantic.ModelGenerator(),
    "sqlalchemy": sqlalchemy.ModelGenerator(),
    "sqlalchemy_core": sqlalchemy_core.ModelGenerator(),
    "sqlmodel": sqlmodel.ModelGenerator(),
    "dataclass": dataclass.ModelGenerator(),
}
```

## API

### Программный интерфейс

```python
from omymodels import create_models, convert_models

# Генерация из DDL
result = create_models(
    ddl="CREATE TABLE users (...)",  # или ddl_path="schema.sql"
    models_type="pydantic",          # gino, sqlalchemy, dataclass, etc.
    dump=True,                       # сохранить в файл
    dump_path="models.py",
    singular=False,                  # users → User (singularize)
    schema_global=True,              # глобальная схема
    defaults_off=False,              # без defaults
)
# Возвращает: {"metadata": {...}, "code": "..."}

# Конвертация между типами
output = convert_models(
    model_from="@dataclass\nclass User: ...",
    models_type="sqlalchemy"
)
```

### Командная строка

```bash
# Базовое использование
omm schema.sql

# С опциями
omm schema.sql -m pydantic -t models.py

# Флаги:
# -m, --models_type     Тип моделей
# -t, --target          Путь для сохранения
# --no-dump             Вывод в консоль
# --no-global-schema    Схема в table_args
# --defaults-off        Без значений по умолчанию
# -v                    Verbose режим
```

## Зависимости

| Библиотека | Назначение |
|------------|------------|
| simple-ddl-parser | Парсинг SQL DDL |
| table-meta | Унифицированная структура TableMeta |
| py-models-parser | Парсинг Python моделей |
| Jinja2 | Шаблонизация кода |
| pydantic | Валидация данных |

## Поддерживаемые форматы

### Входные форматы
- **SQL DDL**: PostgreSQL, MySQL, MS SQL диалекты
- **Python код**: Pydantic, Dataclasses, SQLAlchemy (для конвертации)

### Выходные форматы

| Формат | Описание |
|--------|----------|
| GinoORM | Async PostgreSQL ORM |
| Pydantic | Валидация и сериализация |
| SQLAlchemy ORM | Классический ORM |
| SQLAlchemy Core | Table API |
| SQLModel | SQLAlchemy + Pydantic |
| Dataclasses | Встроенные Python классы |
| Python Enum | Перечисления |

## Паттерны проектирования

1. **Strategy Pattern** - разные генераторы для разных типов
2. **Template Method** - Jinja2 для финального рендеринга
3. **Factory Pattern** - `get_generator_by_type()`
4. **Pipeline** - парсинг → нормализация → генерация → рендеринг

## Расширение

Добавление нового типа моделей:

1. Создать папку `models/[type]/`
2. Добавить `core.py` с классом `ModelGenerator`
3. Добавить `types.py` с маппингом типов
4. Добавить `templates.py` с шаблонами
5. Добавить `[type].jinja2`
6. Зарегистрировать в `generators.py`

## Структура данных

```
TableMeta (table-meta library)
├── name: str
├── columns: List[Column]
│   ├── name: str
│   ├── type: str
│   ├── nullable: bool
│   ├── default: any
│   ├── size: int | tuple
│   ├── primary_key: bool
│   ├── unique: bool
│   └── references: Dict (FK)
├── primary_key: List[str]
├── indexes: List[Index]
├── constraints: Dict
└── table_schema: str
```
