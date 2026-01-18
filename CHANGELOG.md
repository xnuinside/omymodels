# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-18

### Breaking Changes

- Dropped support for Python 3.7 and 3.8
- Minimum required Python version is now 3.9

### Added

**Pydantic v2 Support**
- New `pydantic_v2` models type with native Pydantic v2 syntax
- Uses `X | None` instead of `Optional[X]`
- Uses `dict | list` for JSON/JSONB types instead of `Json`
- Adds `from __future__ import annotations` for Python 3.9 compatibility
- Nullable fields automatically get `= None` default

**OpenAPI 3 (Swagger) Support**
- Generate OpenAPI 3 schemas from DDL: `create_models(ddl, models_type="openapi3")`
- Convert OpenAPI 3 schemas to Python models: `create_models_from_openapi3(schema)`
- Supports JSON and YAML input (with pyyaml)

**Plugin System for Custom Generators**
- `register_generator()` - register custom generator
- `unregister_generator()` - remove custom generator
- `list_generators()` - list all available generators
- Base classes: `BaseGenerator`, `ORMGenerator`, `DataModelGenerator`
- `TypeConverter` class for type mappings
- Entry points support for auto-discovery
- See examples: `example/custom_generator.py`, `example/extend_builtin_generator.py`

**Pydantic Improvements**
- Field alias support for invalid Python identifiers
- Handle Pydantic reserved names (copy, parse_obj, schema, etc.)
- Support for generated columns (`GENERATED ALWAYS AS`) with `exclude=True`
- `table_prefix` and `table_suffix` parameters for class name customization
- Boolean defaults 0/1 converted to False/True
- Expanded `datetime_now_check` with more SQL datetime keywords
- VARCHAR(n) and CHAR(n) now generate `Field(max_length=n)` for Pydantic validation (issue #48)

**SQLAlchemy 2.0 Support (issue #49)**
- New `sqlalchemy_v2` models type with modern SQLAlchemy 2.0 syntax
- Uses `DeclarativeBase` instead of deprecated `declarative_base()`
- Uses `Mapped[T]` type annotations for columns
- Uses `mapped_column()` instead of `Column()`
- Uses `X | None` union syntax for nullable columns
- Supports all column types, foreign keys, indexes, and constraints

**SQLAlchemy Relationships (issue #47)**
- New `relationships` parameter for `create_models()` to generate `relationship()` with `back_populates`
- Automatically generates bidirectional relationships for foreign keys:
  - Parent side (one-to-many): collection attribute pointing to children
  - Child side (many-to-one): attribute pointing to parent
- Works with both `sqlalchemy` and `sqlalchemy_v2` model types
- For `sqlalchemy_v2`: uses `Mapped[List[T]]` for one-to-many and `Mapped[T]` for many-to-one

**Schema-Separated Model Files (issue #40)**
- New `split_by_schema` parameter for `create_models()` to generate separate files per database schema
- Each schema gets its own file with a schema-specific Base class (e.g., `Schema1Base`)
- Tables without explicit schema go to a file with the default `Base` class
- Works with both `sqlalchemy` and `sqlalchemy_v2` model types
- File naming: `{schema_name}_{base_filename}.py` (e.g., `schema1_models.py`)

**SQLModel Improvements**
- Fixed array type generation (issue #66)
- Arrays now properly generate `List[T]` with correct SQLAlchemy ARRAY type
- Added `typing_imports` support for List import
- Added `pydantic_to_sa_fallback` mapping for array element types

**MySQL Support**
- Added blob types support: `tinyblob`, `blob`, `mediumblob`, `longblob` map to `bytes` (issue #62)

**Other**
- Added support for Python 3.12 and 3.13
- Added tox configuration for local multi-version testing (py39-py313)
- Added pytest-cov for code coverage reporting

### Changed

- Simplified datetime imports (`from datetime import datetime` instead of `import datetime`)
- Use `Any` type instead of `Json` for json/jsonb columns in Pydantic
- Enum generation now uses functional syntax: `Enum(value='Name', names=[...])`
- Updated GitHub Actions workflow with latest action versions (checkout@v4, setup-python@v5)
- Updated py-models-parser to version 1.0.0
- Reorganized types module with TypeConverter class

### Fixed

- Fixed dependency conflict with simple-ddl-generator: relaxed `table-meta` constraint to `>=0.1.5` (issue #46)
- Fixed `iterate_over_the_list()` modifying list during iteration
- Fixed meaningless condition in dataclass generator
- Fixed incorrect column type crash (PR #63)
- Fixed enums including whitespace in values (issue #69)
- Fixed boolean values capitalization - now generates `True`/`False` instead of `true`/`false` (PR #67)
- Fixed SQLModel array type generation TypeError (issue #66)
- Fixed MySQL blob types not mapping to `bytes` (issue #62)
- Fixed `sqlalchemy_core` generator missing column names in output
- Fixed `sqlalchemy_core` generator not including type name with size (e.g., `String(255)`)
- Fixed `sqlalchemy_core` generator ForeignKey positional argument order

### Documentation

- Added ARCHITECTURE.md with project documentation
- Updated documentation with Pydantic v2 examples

## [0.17.0]

### Fixed

- Fix character varying type (issue #59)

### Changed

- SQLAlchemy import removed from generation in SQLModels if it is not used
- `= Field()` is not placed in SQLModel if there is no defaults or other settings

## [0.16.0]

### Added

- Initial SQLModel Support

## [0.15.1]

### Changed

- Foreign Key processing updates (PR #55)
- Move to simple-ddl-parser version 1.X

## [0.14.0]

### Added

- Python 3.11 support

## [0.13.0]

### Added

- Added argument `schema_global=` to support SQLAlchemy & Gino different table schemas (issue #41)

## [0.12.1]

### Fixed

- `current_timestamp` function processed now same way as `now()` function from DDL

## [0.12.0]

### Fixed

- Named arguments always go after positional (issue #35)

### Added

- Availability to disable auto-name conversion (issue #36)
- `no_auto_snake_case=True` keeps names 1-to-1 as in DDL file

## [0.11.1]

### Added

- Added bytes type to pydantic (PR #31)

### Changed

- Parser version updated to the latest

## [0.11.0]

### Fixed

- MSSQL column & table names in `[]` now parsed validly (issue #28)
- Names like `users_WorkSchedule` now converted correctly to PascalCase

## [0.10.1]

### Changed

- Update simple-ddl-parser version to 0.21.2

## [0.10.0]

### Changed

- Meta models moved to separate package (table-meta)
- `common` module renamed to `from_ddl`

### Fixed

- Fixed bugs in converter (still in beta)
- Can generate Enum models if DDL has only CREATE TYPE statements
- String enums now inherit from `(str, Enum)` in all model types

### Added

- Converter feature to convert one model type to another (excluding SQLAlchemy Core Tables)

## [0.9.0]

### Added

- Beta models converter from one type of models to another
- If O!MyModels does not know how to convert type - leaves it as is

### Fixed

- In Dataclass & Pydantic generators Decimals & Floats converted to float (previously was int)

## [0.8.4]

### Changed

- If tables not found in DDL - raises NoTable error
- Added `exit_silent` flag for silent exit if no tables

## [0.8.3]

### Added

- TableMetaModel class for unified metadata parsing

### Fixed

- `NOW()` recognized as `now()` (issue #18)
- Default value of `now()` uses field for dataclass (issue #19)

## [0.8.1]

### Fixed

- Parser version updated (fixed several issues)
- Fixed Unique Constraint after schema in SQLAlchemy Core

## [0.8.0]

### Fixed

- `--defaults-off` flag in CLI

### Added

- Support for SQLAlchemy Core Tables generating
- Added examples folder

### Fixed

- ForeignKey in SQLAlchemy

## [0.7.0]

### Added

- SQLAlchemy models generation (defaults as 'server_default')
- Defaults for Pydantic models
- `defaults_off=True` flag and `--defaults-off` CLI flag

### Fixed

- Enum types with lower case names in DDLs
- Dataclass generation issues (default with datetime & Enums)
- Quotes not removed from defaults

## [0.6.0]

### Added

- Python Dataclass generation from DDL
- ForeignKey generation to GinoORM Models with ondelete/onupdate support

## [0.5.0]

### Added

- Enums/IntEnums types for Gino & Pydantic
- UUID type
- `schema_global` key (default True)
- `--no-global-schema` CLI flag

### Changed

- Primary key columns don't show nullable argument

## [0.4.1]

### Fixed

- Table names containing multiple '-'

## [0.4.0]

### Added

- Pydantic models generation from DDL

### Changed

- `create_gino_models` renamed to `create_models`

## [0.3.0]

### Fixed

- Generated Index for 'index' statement (not unique constraint)
- Column size as tuple (4,2)

## [0.2.0]

### Added

- Valid generating columns: autoincrement, default, type, arrays, unique, primary key
- Creating `__table_args__` for indexes
