# O! My Models - Architecture Improvement Suggestions

## Core Idea

Clear separation into two phases:
1. **Parser** - parses input data (DDL, Python models) into unified `TableMeta` structure
2. **Generator** - generates output code based on `TableMeta`

```
Input (DDL/Python)  →  Parser  →  TableMeta  →  Generator  →  Output (Python code)
```

---

## 1. Module Restructuring

### Current Structure (Problems)

```
omymodels/
├── from_ddl.py      # Mixed: parsing, normalization, generation, saving
├── converter.py     # Mixed: Python parsing, normalization, generation
├── logic.py         # ORM-specific logic mixed with general logic
├── types.py         # Too much different logic
└── generators.py    # Only routing
```

### Proposed Structure

```
omymodels/
├── __init__.py              # Public API
├── api.py                   # create_models(), convert_models()
│
├── parsing/                 # PARSING (phase 1)
│   ├── __init__.py
│   ├── ddl_parser.py        # DDL → raw dict (simple-ddl-parser)
│   ├── python_parser.py     # Python → raw dict (py-models-parser)
│   └── normalizer.py        # raw dict → List[TableMeta]
│
├── types/                   # TYPES (separate module)
│   ├── __init__.py
│   ├── sql_types.py         # SQL type groups (string_types, integer_types, etc.)
│   ├── converter.py         # TypeConverter class
│   └── registry.py          # Mappings for each framework
│
├── generation/              # GENERATION (phase 2)
│   ├── __init__.py
│   ├── base.py              # BaseGenerator (abstract class)
│   ├── orm_base.py          # ORMGenerator (for Gino, SQLAlchemy, SQLModel)
│   ├── datamodel_base.py    # DataModelGenerator (for Pydantic, Dataclass)
│   ├── renderer.py          # Jinja2 rendering
│   └── registry.py          # Generator registry
│
├── generators/              # CONCRETE GENERATORS (instead of models/)
│   ├── gino/
│   ├── sqlalchemy/
│   ├── sqlalchemy_core/
│   ├── sqlmodel/
│   ├── pydantic/
│   ├── pydantic_v2/
│   ├── dataclass/
│   └── enum/
│
├── helpers.py
├── errors.py
└── cli.py
```

---

## 2. Base Generator Classes

### 2.1 BaseGenerator (abstract)

```python
# omymodels/generation/base.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from table_meta.model import TableMeta

class BaseGenerator(ABC):
    """Base class for all generators."""

    def __init__(self):
        self.imports: set = set()
        self.custom_types: Dict[str, Any] = {}

    @abstractmethod
    def generate_model(
        self,
        table: TableMeta,
        singular: bool = True,
        exceptions: Optional[List] = None,
        **kwargs
    ) -> str:
        """Generate code for a single model."""
        pass

    @abstractmethod
    def create_header(self, tables: List[TableMeta], **kwargs) -> str:
        """Generate file header with imports."""
        pass

    def get_type(self, column_type: str) -> str:
        """Get target type from SQL type."""
        return self.type_converter.convert(column_type)

    def add_custom_type(self, type_name: str, type_def: Any) -> None:
        """Add custom type (enum, etc.)."""
        self.custom_types[type_name] = type_def
```

### 2.2 ORMGenerator (for ORM frameworks)

```python
# omymodels/generation/orm_base.py
from omymodels.generation.base import BaseGenerator

class ORMGenerator(BaseGenerator):
    """Base class for ORM generators (Gino, SQLAlchemy, SQLModel)."""

    def __init__(self):
        super().__init__()
        self.use_func = False          # func.now()
        self.use_dialect = False       # PostgreSQL dialect
        self.constraints = []
        self.indexes = []

    def generate_column(self, column, table, **kwargs) -> str:
        """Generate ORM column definition."""
        # Common logic from current logic.py
        pass

    def setup_column_attributes(self, column, ...) -> str:
        """Setup column attributes (nullable, default, PK, FK)."""
        pass

    def add_table_args(self, table) -> str:
        """Generate __table_args__ with indexes and constraints."""
        pass

    def prepare_column_default(self, column) -> str:
        """Process default values for ORM."""
        # Common code from all ORM generators
        pass
```

### 2.3 DataModelGenerator (for Pydantic, Dataclass)

```python
# omymodels/generation/datamodel_base.py
from omymodels.generation.base import BaseGenerator

class DataModelGenerator(BaseGenerator):
    """Base class for data model generators (Pydantic, Dataclass)."""

    def __init__(self):
        super().__init__()
        self.datetime_import = False
        self.uuid_import = False
        self.typing_imports: set = set()

    def generate_attr(self, column, defaults_off: bool = False) -> str:
        """Generate model attribute."""
        pass

    def get_python_type(self, sql_type: str) -> str:
        """Map SQL type to Python type."""
        pass

    def format_nullable(self, type_str: str) -> str:
        """Format nullable type (Optional[X] or X | None)."""
        pass

    def format_default(self, default_value: Any) -> str:
        """Format default value for Python."""
        pass
```

---

## 3. Parsing Unification

### 3.1 Unified Parser Interface

```python
# omymodels/parsing/__init__.py
from typing import List, Union
from table_meta.model import TableMeta

def parse(
    input_data: str,
    input_type: str = "ddl"  # "ddl" | "python"
) -> List[TableMeta]:
    """
    Universal input data parser.

    Args:
        input_data: DDL string or Python code
        input_type: Input data type

    Returns:
        List of TableMeta objects
    """
    if input_type == "ddl":
        from omymodels.parsing.ddl_parser import parse_ddl
        raw_data = parse_ddl(input_data)
    elif input_type == "python":
        from omymodels.parsing.python_parser import parse_python
        raw_data = parse_python(input_data)
    else:
        raise ValueError(f"Unknown input type: {input_type}")

    from omymodels.parsing.normalizer import normalize
    return normalize(raw_data)
```

### 3.2 Normalizer - Unified Normalization

```python
# omymodels/parsing/normalizer.py
from typing import List, Dict, Any
from table_meta.model import TableMeta, Column

def normalize(raw_data: Dict[str, Any]) -> List[TableMeta]:
    """
    Normalize raw parser data into TableMeta objects.

    Single normalization point for DDL and Python parsers.
    """
    tables = []

    for table_data in raw_data.get("tables", []):
        table = TableMeta(
            name=_clean_name(table_data["name"]),
            columns=[_normalize_column(c) for c in table_data["columns"]],
            primary_key=table_data.get("primary_key", []),
            indexes=table_data.get("indexes", []),
            constraints=table_data.get("constraints", {}),
            table_schema=table_data.get("schema"),
        )
        tables.append(table)

    return tables

def _normalize_column(column_data: Dict) -> Column:
    """Normalize column data."""
    return Column(
        name=_clean_name(column_data["name"]),
        type=_normalize_type(column_data["type"]),
        nullable=column_data.get("nullable", True),
        default=_clean_default(column_data.get("default")),
        size=column_data.get("size"),
        references=column_data.get("references"),
    )
```

---

## 4. Type Handling Unification

### 4.1 TypeConverter Class

```python
# omymodels/types/converter.py
from typing import Optional, Dict, Tuple
from omymodels.types.sql_types import (
    string_types, integer_types, float_types,
    datetime_types, bool_types, json_types
)

class TypeConverter:
    """Converter for SQL types to target framework types."""

    def __init__(self, mapping: Dict[str, str], prefix: str = ""):
        self.mapping = mapping
        self.prefix = prefix
        self._build_lookup()

    def _build_lookup(self):
        """Build lookup table for fast search."""
        self._lookup = {}
        for sql_type, target_type in self.mapping.items():
            self._lookup[sql_type.lower()] = target_type

    def convert(self, sql_type: str) -> str:
        """Convert SQL type to target type."""
        normalized = sql_type.lower().split("(")[0].strip()
        return self._lookup.get(normalized, sql_type)

    def with_size(self, type_str: str, size: Optional[Tuple]) -> str:
        """Add size to type if needed."""
        if size is None:
            return type_str
        if isinstance(size, tuple):
            return f"{type_str}({size[0]}, {size[1]})"
        return f"{type_str}({size})"

    def is_datetime(self, sql_type: str) -> bool:
        """Check if type is datetime."""
        return sql_type.upper() in datetime_types

    def is_json(self, sql_type: str) -> bool:
        """Check if type is JSON."""
        return sql_type.upper() in json_types
```

### 4.2 Type Registry for Each Framework

```python
# omymodels/types/registry.py

# Gino
GINO_TYPES = {
    "varchar": "db.String",
    "text": "db.Text",
    "integer": "db.Integer",
    "bigint": "db.BigInteger",
    "timestamp": "db.TIMESTAMP",
    # ...
}

# SQLAlchemy
SQLALCHEMY_TYPES = {
    "varchar": "sa.String",
    "text": "sa.Text",
    "integer": "sa.Integer",
    # ...
}

# Pydantic
PYDANTIC_TYPES = {
    "varchar": "str",
    "text": "str",
    "integer": "int",
    "bigint": "int",
    "timestamp": "datetime.datetime",
    "json": "dict | list",  # for v2
    # ...
}

def get_type_converter(framework: str) -> TypeConverter:
    """Return TypeConverter for the specified framework."""
    converters = {
        "gino": TypeConverter(GINO_TYPES, prefix="db."),
        "sqlalchemy": TypeConverter(SQLALCHEMY_TYPES, prefix="sa."),
        "pydantic": TypeConverter(PYDANTIC_TYPES),
        "pydantic_v2": TypeConverter(PYDANTIC_V2_TYPES),
        # ...
    }
    return converters[framework]
```

---

## 5. Code Duplication Elimination

### 5.1 Current Duplication (~30-40%)

| Method | Duplicated in | Solution |
|--------|---------------|----------|
| `prepare_column_default()` | Gino, SQLAlchemy, SQLModel, SQLAlchemy Core | Move to `ORMGenerator` |
| `create_header()` (ORM) | Gino, SQLAlchemy, SQLModel | Move to `ORMGenerator` |
| `get_not_custom_type()` | Pydantic, Pydantic v2, Dataclass | Move to `DataModelGenerator` |
| `generate_attr()` | Pydantic, Pydantic v2, Dataclass | Move to `DataModelGenerator` |
| `types_mapping` building | All generators | Use `TypeConverter` |

### 5.2 Refactoring Example

**Before (duplication in 4 files):**
```python
# models/gino/core.py, models/sqlalchemy/core.py, models/sqlmodel/core.py
def prepare_column_default(self, column_data, column):
    if isinstance(column_data.default, str):
        if column_data.type.upper() in datetime_types:
            if datetime_now_check(column_data.default.lower()):
                column_data.default = "func.now()"
                self.state.add("func")
            # ... 20+ lines of identical code
```

**After (once in base class):**
```python
# omymodels/generation/orm_base.py
class ORMGenerator(BaseGenerator):
    def prepare_column_default(self, column) -> str:
        """Process default values for ORM."""
        if column.type.upper() in datetime_types:
            if is_now_function(column.default):
                self.use_func = True
                return "func.now()"
        return self._format_default(column.default)
```

---

## 6. API Improvement

### 6.1 Unified Public API

```python
# omymodels/api.py
from typing import Optional, List, Dict, Any, Union
from pathlib import Path

def generate(
    input_data: Union[str, Path],
    input_type: str = "ddl",           # "ddl" | "python"
    output_type: str = "gino",          # "gino" | "pydantic" | etc.
    output_path: Optional[Path] = None,
    *,
    singular: bool = True,
    schema_global: bool = True,
    defaults_off: bool = False,
    exceptions: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Universal model generation function.

    Args:
        input_data: DDL string, Python code, or file path
        input_type: Input data type
        output_type: Output model type
        output_path: Path for saving (optional)
        singular: Singularize table names
        schema_global: Global schema vs per-table
        defaults_off: Disable default values
        exceptions: Exceptions for singularization

    Returns:
        {"code": str, "metadata": dict}
    """
    # 1. Load data
    if isinstance(input_data, Path):
        input_data = input_data.read_text()

    # 2. Parse
    from omymodels.parsing import parse
    tables = parse(input_data, input_type)

    # 3. Generate
    from omymodels.generation.registry import get_generator
    generator = get_generator(output_type)
    code = generator.generate_all(
        tables,
        singular=singular,
        schema_global=schema_global,
        defaults_off=defaults_off,
        exceptions=exceptions,
    )

    # 4. Save
    if output_path:
        output_path.write_text(code)

    return {"code": code, "metadata": {"tables": len(tables)}}


# Backward compatibility
def create_models(ddl: str, **kwargs) -> Dict[str, Any]:
    """Backward compatible wrapper."""
    return generate(ddl, input_type="ddl", **kwargs)

def convert_models(python_code: str, **kwargs) -> str:
    """Backward compatible wrapper."""
    result = generate(python_code, input_type="python", **kwargs)
    return result["code"]
```

---

## 7. Bug Fixes

### 7.1 iterate_over_the_list() - List Modification During Iteration

**Current code (bug):**
```python
def iterate_over_the_list(items: List) -> str:
    for item in items:
        if isinstance(item, str):
            items.append(clean_value(item))
            items.remove(item)  # Modification during iteration!
    return items
```

**Fix:**
```python
def iterate_over_the_list(items: List) -> List:
    return [
        clean_value(item) if isinstance(item, str)
        else prepare_data(item) if isinstance(item, dict)
        else item
        for item in items
    ]
```

### 7.2 dataclass/core.py - Meaningless Condition

**Current code:**
```python
if _type == _type:  # Always True!
    _type = types_mapping.get(_type, _type)
```

**Fix:**
```python
_type = types_mapping.get(_type, _type)
```

---

## 8. Feature Extensions

### 8.1 New SQL Type Support

- `INTERVAL` - for time intervals
- `POINT`, `POLYGON` - geometric types (PostGIS)
- `ARRAY` - improved multi-dimensional array support
- `HSTORE` - PostgreSQL key-value
- `INET`, `CIDR` - network types

### 8.2 New Target Frameworks

- **Tortoise ORM** - async ORM
- **Django ORM** - popular web framework
- **Peewee** - lightweight ORM
- **attrs** - dataclasses alternative
- **msgspec** - fast serialization

### 8.3 Additional Features

- **Pydantic validators** - auto-generation from constraints
- **Alembic migrations** - migration generation
- **TypedDict** - for JSON schemas
- **Protocol classes** - for interfaces

---

## 9. Plugin System for Custom Generators

Allow users to register their own generators without forking the repository.

### 9.1 Generator Registration API

```python
# omymodels/plugins.py
from typing import Type, Dict
from omymodels.generation.base import BaseGenerator

_custom_generators: Dict[str, Type[BaseGenerator]] = {}

def register_generator(name: str, generator_class: Type[BaseGenerator]) -> None:
    """
    Register a custom generator.

    Args:
        name: Unique generator name (e.g., "my_orm", "custom_pydantic")
        generator_class: Generator class inheriting from BaseGenerator

    Example:
        from omymodels import register_generator
        from omymodels.generation.base import BaseGenerator

        class MyORMGenerator(BaseGenerator):
            ...

        register_generator("my_orm", MyORMGenerator)
    """
    if not issubclass(generator_class, BaseGenerator):
        raise TypeError(f"{generator_class} must inherit from BaseGenerator")
    _custom_generators[name] = generator_class

def unregister_generator(name: str) -> None:
    """Remove a custom generator."""
    _custom_generators.pop(name, None)

def get_generator(name: str) -> BaseGenerator:
    """Get generator by name (built-in or custom)."""
    if name in _custom_generators:
        return _custom_generators[name]()
    from omymodels.generation.registry import builtin_generators
    if name in builtin_generators:
        return builtin_generators[name]()
    raise ValueError(f"Unknown generator: {name}")
```

### 9.2 User-Defined Generator Example

```python
# my_project/generators/peewee_generator.py
from omymodels.generation.base import BaseGenerator
from omymodels.types.converter import TypeConverter
from table_meta.model import TableMeta

# Type mapping for Peewee
PEEWEE_TYPES = {
    "varchar": "CharField",
    "text": "TextField",
    "integer": "IntegerField",
    "bigint": "BigIntegerField",
    "boolean": "BooleanField",
    "timestamp": "DateTimeField",
    "date": "DateField",
    "float": "FloatField",
    "decimal": "DecimalField",
    "uuid": "UUIDField",
    "json": "JSONField",
}

class PeeweeGenerator(BaseGenerator):
    """Custom generator for Peewee ORM."""

    def __init__(self):
        super().__init__()
        self.type_converter = TypeConverter(PEEWEE_TYPES)
        self.imports = {"peewee"}

    def generate_model(self, table: TableMeta, singular: bool = True, **kwargs) -> str:
        """Generate Peewee model class."""
        class_name = self._to_class_name(table.name, singular)

        lines = [f"\nclass {class_name}(Model):"]

        for column in table.columns:
            field_type = self.type_converter.convert(column.type)
            attrs = self._get_field_attrs(column)
            lines.append(f"    {column.name} = {field_type}({attrs})")

        # Meta class
        lines.append("")
        lines.append("    class Meta:")
        lines.append(f"        table_name = '{table.name}'")

        return "\n".join(lines)

    def create_header(self, tables, **kwargs) -> str:
        """Generate imports."""
        fields = set()
        for table in tables:
            for col in table.columns:
                fields.add(self.type_converter.convert(col.type))

        return f"from peewee import Model, {', '.join(sorted(fields))}\n"

    def _to_class_name(self, name: str, singular: bool) -> str:
        """Convert table name to class name."""
        # Simple implementation
        return "".join(word.capitalize() for word in name.split("_"))

    def _get_field_attrs(self, column) -> str:
        """Generate field attributes."""
        attrs = []
        if column.nullable:
            attrs.append("null=True")
        if column.default is not None:
            attrs.append(f"default={column.default!r}")
        return ", ".join(attrs)
```

### 9.3 Using Custom Generator

```python
# my_project/main.py
from omymodels import create_models, register_generator
from my_project.generators.peewee_generator import PeeweeGenerator

# Register custom generator
register_generator("peewee", PeeweeGenerator)

# Use it
ddl = """
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
"""

result = create_models(ddl, models_type="peewee")
print(result["code"])

# Output:
# from peewee import Model, CharField, DateTimeField, IntegerField
#
# class Users(Model):
#     id = IntegerField()
#     name = CharField()
#     email = CharField(null=True)
#     created_at = DateTimeField(default=datetime.datetime.now)
#
#     class Meta:
#         table_name = 'users'
```

### 9.4 Entry Points for Auto-Discovery

Support automatic discovery via `pyproject.toml` entry points:

```toml
# In user's pyproject.toml
[project.entry-points."omymodels.generators"]
peewee = "my_package.generators:PeeweeGenerator"
django = "my_package.generators:DjangoGenerator"
```

```python
# omymodels/plugins.py
import sys
if sys.version_info >= (3, 10):
    from importlib.metadata import entry_points
else:
    from importlib_metadata import entry_points

def discover_plugins() -> None:
    """Auto-discover generators from entry points."""
    eps = entry_points(group="omymodels.generators")
    for ep in eps:
        generator_class = ep.load()
        register_generator(ep.name, generator_class)

# Call on import
discover_plugins()
```

### 9.5 Generator Inheritance for Quick Customization

Users can extend built-in generators:

```python
from omymodels.generation.pydantic_v2 import PydanticV2Generator

class MyPydanticGenerator(PydanticV2Generator):
    """Pydantic v2 with custom JSON handling."""

    def __init__(self):
        super().__init__()
        # Override JSON type to use specific TypedDict
        self.type_converter.mapping["json"] = "JsonData"
        self.type_converter.mapping["jsonb"] = "JsonData"

    def create_header(self, tables, **kwargs) -> str:
        header = super().create_header(tables, **kwargs)
        # Add custom import
        return "from my_types import JsonData\n" + header

register_generator("my_pydantic", MyPydanticGenerator)
```

### 9.6 CLI Support for Custom Generators

```bash
# Register via environment variable
export OMYMODELS_PLUGINS="my_package.generators"

# Or via config file (~/.omymodels.toml)
[plugins]
generators = ["my_package.generators.PeeweeGenerator"]

# Use in CLI
omm schema.sql -m peewee -t models.py
```

### 9.7 Validation and Error Handling

```python
# omymodels/plugins.py
from omymodels.generation.base import BaseGenerator

def register_generator(name: str, generator_class: Type[BaseGenerator]) -> None:
    """Register with validation."""
    # Validate inheritance
    if not issubclass(generator_class, BaseGenerator):
        raise TypeError(
            f"Generator must inherit from BaseGenerator, "
            f"got {generator_class.__bases__}"
        )

    # Validate required methods
    required_methods = ["generate_model", "create_header"]
    for method in required_methods:
        if not hasattr(generator_class, method):
            raise TypeError(f"Generator missing required method: {method}")

    # Validate name
    if not name.isidentifier():
        raise ValueError(f"Invalid generator name: {name!r}")

    # Check for conflicts with built-in
    from omymodels.generation.registry import builtin_generators
    if name in builtin_generators:
        raise ValueError(
            f"Cannot override built-in generator: {name}. "
            f"Use a different name."
        )

    _custom_generators[name] = generator_class
```

### 9.8 Public API Additions

```python
# omymodels/__init__.py
from omymodels.plugins import (
    register_generator,
    unregister_generator,
    list_generators,
)
from omymodels.generation.base import BaseGenerator
from omymodels.generation.orm_base import ORMGenerator
from omymodels.generation.datamodel_base import DataModelGenerator
from omymodels.types.converter import TypeConverter

__all__ = [
    # Existing
    "create_models",
    "convert_models",
    # New plugin API
    "register_generator",
    "unregister_generator",
    "list_generators",
    # Base classes for extension
    "BaseGenerator",
    "ORMGenerator",
    "DataModelGenerator",
    "TypeConverter",
]
```

---

## 10. Testing Improvements

### 10.1 Test Structure

```
tests/
├── unit/
│   ├── parsing/
│   │   ├── test_ddl_parser.py
│   │   ├── test_python_parser.py
│   │   └── test_normalizer.py
│   ├── types/
│   │   ├── test_converter.py
│   │   └── test_registry.py
│   └── generation/
│       ├── test_base_generator.py
│       ├── test_orm_generator.py
│       └── test_datamodel_generator.py
│
├── functional/
│   └── generators/
│       ├── test_gino.py
│       ├── test_sqlalchemy.py
│       ├── test_pydantic.py
│       └── ...
│
├── integration/
│   ├── test_full_pipeline.py      # DDL → TableMeta → Code
│   └── test_runtime_validation.py  # Generated code works
│
└── fixtures/
    ├── ddl/
    │   ├── simple.sql
    │   ├── with_fk.sql
    │   └── complex.sql
    └── expected/
        ├── gino/
        ├── pydantic/
        └── ...
```

### 10.2 Property-based Tests

```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1, alphabet=st.characters(whitelist_categories=('L',))))
def test_table_name_normalization(name):
    """Any table name should normalize to a valid Python identifier."""
    result = normalize_table_name(name)
    assert result.isidentifier()
```

---

## 11. Implementation Plan

### Phase 1: Base Infrastructure (1-2 weeks)
1. Create `omymodels/generation/base.py` with `BaseGenerator`
2. Create `omymodels/types/converter.py` with `TypeConverter`
3. Fix discovered bugs
4. Add tests for new classes

### Phase 2: ORM Generators (1-2 weeks)
1. Create `ORMGenerator` with common logic
2. Refactor Gino, SQLAlchemy, SQLModel to use inheritance
3. Remove duplicate code
4. Update tests

### Phase 3: Data Model Generators (1 week)
1. Create `DataModelGenerator`
2. Refactor Pydantic, Pydantic v2, Dataclass
3. Remove duplicate code

### Phase 4: Parsing Unification (1 week)
1. Create `omymodels/parsing/` module
2. Extract normalization to `normalizer.py`
3. Update `from_ddl.py` and `converter.py`

### Phase 5: Finalization (1 week)
1. Update public API
2. Update documentation
3. Ensure backward compatibility
4. Full testing

---

## 12. Expected Results

| Metric | Before | After |
|--------|--------|-------|
| Code duplication | ~35% | ~10% |
| Lines of code | 2348 | ~1800 |
| Time to add generator | 2-3 hours | 30-60 min |
| Test coverage | ~60% | ~85% |
| Number of base classes | 0 | 3 |
