from typing import Dict
from table_meta.model import Column

postgresql_dialect = ["ARRAY", "JSON", "JSONB", "UUID"]

string_types = (
    "str",
    "varchar",
    "character",
    "character_vying",
    "varying",
    "char",
    "string",
    "String",
)

text_types = ("text", "Text")
datetime_types = (
    "DATETIME",
    "time",
    "datetime.datetime",
    "datetime",
    "datetime.date",
    "date",
)

json_types = ("union[dict, list]", "json", "union")

integer_types = ("integer", "int", "serial")

big_integer_types = ("bigint", "bigserial")

float_types = ("float",)

numeric_types = ("decimal", "numeric", "double")

boolean_types = ("boolean", "bool")

datetime_types = (
    "TIMESTAMP",
    "DATETIME",
    "DATE",
    "datetime.datetime",
    "datetime",
    "datetime.date",
    "date",
)


def populate_types_mapping(mapper: Dict) -> Dict:
    types_mapping = {}
    for type_group, value in mapper.items():
        for type_ in type_group:
            types_mapping[type_] = value
    return types_mapping


def prepare_type(column_data: Dict, models_types_mapping: Dict) -> str:
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


def process_types_after_models_parser(column_data: Column) -> Column:
    if "." in column_data.type:
        column_data.type = column_data.type.split(".")[1]
    if "(" in column_data.type:
        if "Enum" not in column_data.type:
            column_data.type = column_data.type.split("(")[0]
        else:
            column_data.type = column_data.type.split("Enum(")[1].replace(")", "")
    column_data.type = column_data.type.lower()
    return column_data


def prepare_column_data(column_data: Column) -> str:
    if "." in column_data.type or "(":
        column_data = process_types_after_models_parser(column_data)
    return column_data


def prepare_column_type_orm(obj: object, column_data: Column) -> str:
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
