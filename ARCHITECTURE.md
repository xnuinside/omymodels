# O! My Models - Project Architecture

## Overview

**O! My Models (omymodels)** - a universal Python library for:
- Generating ORM models from SQL DDL (CREATE TABLE)
- Converting models between different frameworks (Pydantic → SQLAlchemy, etc.)

**Version:** 1.0.0
**Python:** >=3.9
**License:** MIT

## Project Structure

```
omymodels/
├── __init__.py              # Public API: create_models(), convert_models()
├── from_ddl.py              # Main DDL generation module
├── converter.py             # Converter between model types
├── cli.py                   # Command line interface (omm)
├── generators.py            # Router to generators
├── helpers.py               # Utilities (pluralize, snake_case, etc.)
├── logic.py                 # Column and table generation logic
├── errors.py                # Exceptions
├── types.py                 # Base SQL type definitions
├── plugins.py               # Plugin system for custom generators
├── openapi.py               # OpenAPI 3 schema conversion
│
├── generation/              # Base generator classes
│   ├── base.py              # BaseGenerator abstract class
│   ├── datamodel_base.py    # Base for data models (Pydantic, Dataclass)
│   └── orm_base.py          # Base for ORM models (SQLAlchemy, Gino)
│
└── models/                  # Generators for each model type
    ├── gino/                # GinoORM (async PostgreSQL)
    ├── pydantic/            # Pydantic v1 (validation, Optional[X])
    ├── pydantic_v2/         # Pydantic v2 (validation, X | None)
    ├── sqlalchemy/          # SQLAlchemy ORM
    ├── sqlalchemy_core/     # SQLAlchemy Core (Table API)
    ├── sqlmodel/            # SQLModel (SQLAlchemy + Pydantic)
    ├── dataclass/           # Python Dataclasses
    ├── enum/                # Python Enum
    ├── openapi3/            # OpenAPI 3 schema generator
    ├── pydal/               # PyDAL (in development)
    └── tortoise/            # Tortoise ORM (in development)
```

Each generator contains:
- `core.py` - ModelGenerator class
- `types.py` - SQL → target type mapping
- `templates.py` - code string templates
- `*.jinja2` - final file template

## Architecture

### Data Flow

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
│  - TableMeta objects        │
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│  Type Conversion            │
│  - types.py mapping         │
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

### Key Components

#### 1. ModelGenerator (models/*/core.py)

Base generator structure:

```python
class ModelGenerator:
    def __init__(self):
        self.types_mapping      # SQL → target type
        self.templates          # Code templates
        self.state              # Import tracking
        self.custom_types       # Enum and custom types

    def generate_model(table)   # Generate single model
    def create_header(tables)   # Header with imports
```

#### 2. Type System (types.py)

SQL type groups:
- `string_types`: VARCHAR, CHAR, TEXT, STRING
- `integer_types`: INTEGER, INT, SERIAL, BIGINT, SMALLINT
- `datetime_types`: DATE, TIMESTAMP, DATETIME, TIME
- `bool_types`: BOOLEAN, BOOL
- `float_types`: FLOAT, DECIMAL, NUMERIC, DOUBLE
- `json_types`: JSON, JSONB

#### 3. Generation Logic (logic.py)

- `generate_column()` - complete column definition
- `setup_column_attributes()` - nullable, defaults, primary_key
- `add_table_args()` - indexes, constraints, schema
- `add_reference_to_the_column()` - foreign keys

#### 4. Router (generators.py)

```python
models = {
    "gino": gino.ModelGenerator(),
    "pydantic": pydantic.ModelGenerator(),
    "pydantic_v2": pydantic_v2.ModelGenerator(),
    "sqlalchemy": sqlalchemy.ModelGenerator(),
    "sqlalchemy_core": sqlalchemy_core.ModelGenerator(),
    "sqlmodel": sqlmodel.ModelGenerator(),
    "dataclass": dataclass.ModelGenerator(),
    "openapi3": openapi3.ModelGenerator(),
}
```

## API

### Programmatic Interface

```python
from omymodels import create_models, convert_models

# Generate from DDL
result = create_models(
    ddl="CREATE TABLE users (...)",  # or ddl_path="schema.sql"
    models_type="pydantic",          # gino, sqlalchemy, dataclass, etc.
    dump=True,                       # save to file
    dump_path="models.py",
    singular=False,                  # users → User (singularize)
    schema_global=True,              # global schema
    defaults_off=False,              # without defaults
)
# Returns: {"metadata": {...}, "code": "..."}

# Convert between types
output = convert_models(
    model_from="@dataclass\nclass User: ...",
    models_type="sqlalchemy"
)
```

### Command Line

```bash
# Basic usage
omm schema.sql

# With options
omm schema.sql -m pydantic -t models.py

# Flags:
# -m, --models_type     Model type
# -t, --target          Save path
# --no-dump             Output to console
# --no-global-schema    Schema in table_args
# --defaults-off        Without default values
# -v                    Verbose mode
```

## Dependencies

| Library | Purpose |
|---------|---------|
| simple-ddl-parser | SQL DDL parsing |
| table-meta | Unified TableMeta structure |
| py-models-parser | Python model parsing |
| Jinja2 | Code templating |
| pydantic | Data validation |

## Supported Formats

### Input Formats
- **SQL DDL**: PostgreSQL, MySQL, MS SQL dialects
- **Python code**: Pydantic, Dataclasses, SQLAlchemy (for conversion)
- **OpenAPI 3**: JSON/YAML schema definitions

### Output Formats

| Format | Description |
|--------|-------------|
| GinoORM | Async PostgreSQL ORM |
| Pydantic v1 | Validation and serialization (Optional[X]) |
| Pydantic v2 | Validation and serialization (X \| None) |
| SQLAlchemy ORM | Classic ORM |
| SQLAlchemy Core | Table API |
| SQLModel | SQLAlchemy + Pydantic |
| Dataclasses | Built-in Python classes |
| Python Enum | Enumerations |
| OpenAPI 3 | JSON schema definitions |

## Design Patterns

1. **Strategy Pattern** - different generators for different types
2. **Template Method** - Jinja2 for final rendering
3. **Factory Pattern** - `get_generator_by_type()`
4. **Pipeline** - parsing → normalization → generation → rendering

## Extension

### Adding a New Model Type

1. Create folder `models/[type]/`
2. Add `core.py` with `ModelGenerator` class
3. Add `types.py` with type mapping
4. Add `templates.py` with templates
5. Add `[type].jinja2`
6. Register in `generators.py`

### Plugin System

Custom generators can be registered without forking:

```python
from omymodels import register_generator
from omymodels.generation import BaseGenerator

class MyORMGenerator(BaseGenerator):
    def generate_model(self, table, **kwargs):
        ...
    def create_header(self, tables, **kwargs):
        ...

register_generator("my_orm", MyORMGenerator)
```

Or via entry points in `pyproject.toml`:

```toml
[project.entry-points."omymodels.generators"]
my_orm = "my_package.generators:MyORMGenerator"
```

## Data Structure

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
