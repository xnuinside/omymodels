"""Types module for omymodels.

Provides SQL type definitions and type conversion utilities.
"""

from typing import Dict

from table_meta.model import Column

from omymodels.types.converter import TypeConverter
from omymodels.types.sql_types import (
    ALL_TYPE_GROUPS,
    big_integer_types,
    binary_types,
    boolean_types,
    datetime_types,
    float_types,
    integer_types,
    json_types,
    numeric_types,
    postgresql_dialect,
    string_types,
    text_types,
    uuid_types,
)

__all__ = [
    "TypeConverter",
    "postgresql_dialect",
    "string_types",
    "text_types",
    "binary_types",
    "json_types",
    "integer_types",
    "big_integer_types",
    "float_types",
    "numeric_types",
    "boolean_types",
    "datetime_types",
    "uuid_types",
    "ALL_TYPE_GROUPS",
    # Legacy functions for backward compatibility
    "populate_types_mapping",
    "prepare_type",
    "add_custom_type_orm",
    "set_column_size",
    "add_size_to_orm_column",
    "process_types_after_models_parser",
    "prepare_column_data",
    "prepare_column_type_orm",
]


# Legacy functions for backward compatibility
def populate_types_mapping(mapper: Dict) -> Dict:
    """Build type mapping from type groups."""
    types_mapping = {}
    for type_group, value in mapper.items():
        for type_ in type_group:
            types_mapping[type_] = value
    return types_mapping


def prepare_type(column_data, models_types_mapping: Dict) -> str:
    """Get target type for column from mapping."""
    column_type = None
    column_data_type = column_data.type.lower().split("[")[0]
    if not column_type:
        column_type = models_types_mapping.get(column_data_type, column_type)
    if not column_type:
        column_type = column_data_type
    return column_type


def add_custom_type_orm(
    custom_types: Dict, column_data_type: str, column_type: str
) -> str:
    """Handle custom types (enums) for ORM generators."""
    if "." in column_data_type:
        column_data_type = column_data_type.split(".")[1]
    column_type = custom_types.get(column_data_type, column_type)

    if isinstance(column_type, tuple):
        column_data_type = column_type[1]
        column_type = column_type[0]
    if column_type is not None:
        column_type = f"{column_type}({column_data_type})"
    return column_type


def set_column_size(column_type: str, column_data) -> str:
    """Add size to column type."""
    if isinstance(column_data.size, int):
        column_type += f"({column_data.size})"
    elif isinstance(column_data.size, tuple):
        column_type += f"({','.join([str(x) for x in column_data.size])})"
    return column_type


def add_size_to_orm_column(column_type: str, column_data) -> str:
    """Add size or empty parens to ORM column type."""
    if column_data.size:
        column_type = set_column_size(column_type, column_data)
    elif column_type != "UUID" and "(" not in column_type:
        column_type += "()"
    return column_type


def process_types_after_models_parser(column_data: Column) -> Column:
    """Process column type from Python models parser."""
    if "." in column_data.type:
        column_data.type = column_data.type.split(".")[1]
    if "(" in column_data.type:
        if "Enum" not in column_data.type:
            column_data.type = column_data.type.split("(")[0]
        else:
            column_data.type = column_data.type.split("Enum(")[1].replace(")", "")
    column_data.type = column_data.type.lower()
    return column_data


def prepare_column_data(column_data: Column) -> Column:
    """Prepare column data for generation."""
    if "." in column_data.type or "(":
        column_data = process_types_after_models_parser(column_data)
    return column_data


def prepare_column_type_orm(obj: object, column_data: Column) -> str:
    """Prepare column type for ORM generators."""
    column_type = None
    column_data = prepare_column_data(column_data)
    if obj.custom_types:
        column_type = add_custom_type_orm(
            obj.custom_types, column_data.type, column_type
        )
    if not column_type:
        column_type = prepare_type(column_data, obj.types_mapping)
    if column_type in postgresql_dialect:
        obj.postgresql_dialect_cols.add(column_type)

    column_type = add_size_to_orm_column(column_type, column_data)
    if "[" in column_data.type and column_data.type not in json_types:
        obj.postgresql_dialect_cols.add("ARRAY")
        column_type = f"ARRAY({column_type})"
    return column_type
