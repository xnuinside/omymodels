from omymodels.utils import type_not_found
from typing import Dict

postgresql_dialect = ["ARRAY", "JSON", "JSONB", "UUID"]


ddl_types_mapping = {
    "str": "varchar",
    "int": "integer",
    "bool": "boolean",
    "list": "varchar[]",
    "datetime.datetime": "timestamp",
    "datetime.date": "date",
    "dict": "Json",
    "json": "Json",
    "array": "varchar[]",
}

python_types_mapping = {
    "str": "str",
    "int": "int",
    "bool": "bool",
    "list": "list",
    "datetime.datetime": "datetime.datetime",
    "datetime.date": "datetime.date",
    "dict": "dict",
    "Json": "Json",
    "array": "varchar[]",
}

python_typing_complex_types = ["Optional", "List", "Union", "Dict"]

# types that can include another types inside
complex_types = [x.lower() for x in python_typing_complex_types] + ["array"]


def is_type_in_python_complex(_type):
    for c_type in python_typing_complex_types:
        if c_type in _type:
            return _type


def prepare_types(column_type: str) -> str:
    ddl_type = False
    if column_type in python_types_mapping:
        column_type = column_type
    else:
        column_type = is_type_in_python_complex(column_type)
        if not column_type:
            ddl_type = True
            column_type = ddl_types_mapping.get(column_type, column_type)
    if ddl_type:
        column_type = column_type.lower().split("[")[0]
    return column_type, ddl_type


def prepare_type(column_data: Dict, models_types_mapping: Dict) -> str:
    column_type = type_not_found
    column_data_type = column_data.type.lower().split("[")[0]
    if column_type == type_not_found:
        column_type = models_types_mapping.get(column_data_type, column_type)
    return column_type


def add_custom_type_orm(
    custom_types: Dict, column_data_type: str, column_type: str
) -> str:
    if "." in column_data_type:
        column_data_type = column_data_type.split(".")[1]
    column_type = custom_types.get(column_data_type, column_type)
    if isinstance(column_type, tuple):
        column_data_type = column_type[1]
        column_type = column_type[0]
    if column_type is not None:
        column_type = f"{column_type}({column_data_type})"
    return column_type


def set_column_size(column_type: str, column_data: Dict) -> str:
    if isinstance(column_data.size, int):
        column_type += f"({column_data.size})"
    elif isinstance(column_data.size, tuple):
        column_type += f"({','.join([str(x) for x in column_data.size])})"
    return column_type


def add_size_to_orm_column(column_type: str, column_data: Dict) -> str:
    if column_data.size:
        column_type = set_column_size(column_type, column_data)
    elif column_type != "UUID" and "(" not in column_type:
        column_type += "()"
    return column_type


def prepare_column_type_orm(obj: object, column_data: Dict) -> str:
    column_type = None
    if obj.custom_types:
        column_type = add_custom_type_orm(
            obj.custom_types, column_data.type, column_type
        )
    if not column_type:
        column_type = prepare_type(column_data, obj.types_mapping)
    if column_type in postgresql_dialect:
        obj.postgresql_dialect_cols.add(column_type)

    column_type = add_size_to_orm_column(column_type, column_data)
    if "[" in column_data.type:
        obj.postgresql_dialect_cols.add("ARRAY")
        column_type = f"ARRAY({column_type})"
    return column_type
