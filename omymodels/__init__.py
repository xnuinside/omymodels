"""O! My Models - Generate Python models from SQL DDL.

Supports generating models for:
- SQLAlchemy ORM and Core
- GinoORM
- Pydantic v1 and v2
- SQLModel
- Python Dataclasses
- OpenAPI 3 schemas
"""

from omymodels.converter import convert_models
from omymodels.from_ddl import create_models
from omymodels.openapi import create_models_from_openapi3

# Plugin system for custom generators
from omymodels.plugins import (
    list_generators,
    register_generator,
    unregister_generator,
)

# Base classes for creating custom generators
from omymodels.generation import (
    BaseGenerator,
    DataModelGenerator,
    ORMGenerator,
)

# Type converter for custom generators
from omymodels.types import TypeConverter

__all__ = [
    # Main API
    "create_models",
    "convert_models",
    "create_models_from_openapi3",
    # Plugin system
    "register_generator",
    "unregister_generator",
    "list_generators",
    # Base classes for custom generators
    "BaseGenerator",
    "ORMGenerator",
    "DataModelGenerator",
    "TypeConverter",
]
