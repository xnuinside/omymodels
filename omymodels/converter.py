from typing import List, Dict

from py_models_parser import parse
from table_meta import TableMeta, Type
from omymodels.generators import get_generator_by_type, render_jinja2_template
from omymodels.helpers import from_class_to_table_name, add_custom_types_to_generator
from omymodels.models.enum import core as enum


def get_primary_keys(columns: List[Dict]) -> List[str]:
    primary_keys = []
    for column in columns:
        if column.get("properties", {}).get("primary_key"):
            primary_keys.append(column["name"])
    return primary_keys


def prepare_columns_data(columns: List[Dict]) -> List[Dict]:
    for column in columns:
        if column["type"] is None:
            if column["default"]:
                column["type"] = type(column["default"]).__name__
    return columns


def models_to_meta(data: List[Dict]) -> List[TableMeta]:
    tables = []
    types = []
    for model in data:
        if "Enum" not in model["parents"]:
            model["table_name"] = from_class_to_table_name(model["name"])
            model["columns"] = prepare_columns_data(model["attrs"])
            model["properties"]["indexes"] = model["properties"].get("indexes") or []
            model["primary_key"] = get_primary_keys(model["columns"])
            tables.append(TableMeta(**model))
        else:
            model["type_name"] = model["name"]
            model["base_type"] = model["parents"][-1]
            types.append(Type(**model))
    return tables, types


def convert_models(model_from: str, models_type: str = "gino") -> str:
    result = parse(model_from)
    tables, types = models_to_meta(result)
    generator = get_generator_by_type(models_type)
    models_str = ""
    header = ""
    if types:
        types_generator = enum.ModelGenerator(types)
        models_str += types_generator.create_types()
        header += types_generator.create_header()
    if tables:

        add_custom_types_to_generator(types, generator)

        for table in tables:
            models_str += generator.generate_model(table)
        header += generator.create_header(tables)
    else:
        header += enum.create_header(generator.enum_imports)
        models_type = "enum"
    output = render_jinja2_template(models_type, models_str, header)
    return output
