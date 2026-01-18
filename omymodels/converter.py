from typing import Dict, List

from py_models_parser import parse
from table_meta import TableMeta, Type

from omymodels.generators import get_generator_by_type, render_jinja2_template
from omymodels.helpers import add_custom_types_to_generator, from_class_to_table_name
from omymodels.models.enum import core as enum


def _strip_quotes(value: str) -> str:
    """Strip surrounding quotes from a string value."""
    if value and isinstance(value, str):
        return value.strip("'\"")
    return value


def _is_pydal_result(data: List[Dict]) -> bool:
    """Check if parsed data is from Pydal (names contain quotes)."""
    if data and data[0].get("name", ""):
        name = data[0]["name"]
        return name.startswith(("'", '"')) and name.endswith(("'", '"'))
    return False


def _process_pydal_type(col_type: str, attr: Dict) -> str:
    """Process Pydal column type and handle special types.

    - 'id' type: Pydal's auto-generated primary key (maps to integer + primary_key)
    - 'reference table_name': Foreign key to another table (maps to integer + FK)
    """
    if col_type == "id":
        # Pydal 'id' type is auto-generated primary key
        attr["properties"]["primary_key"] = True
        return "integer"

    if col_type and col_type.startswith("reference "):
        ref_table = col_type.split(" ", 1)[1].strip()
        # Store reference info for foreign key generation
        # All keys expected by add_reference_to_the_column must be present
        attr["references"] = {
            "table": ref_table,
            "column": "id",  # Pydal references default to 'id' column
            "schema": None,
            "on_delete": None,
            "on_update": None,
        }
        return "integer"  # Reference fields are integers

    return col_type


def _clean_pydal_data(data: List[Dict]) -> List[Dict]:
    """Clean Pydal parsed data by stripping quotes from names and types.

    For Pydal, the model name is already the table name, so we set table_name
    directly to avoid incorrect pluralization.
    """
    for model in data:
        table_name = _strip_quotes(model.get("name", ""))
        model["name"] = table_name
        # For Pydal, the name is already the table name - mark it to skip pluralization
        model["table_name"] = table_name
        for attr in model.get("attrs", []):
            attr["name"] = _strip_quotes(attr.get("name", ""))
            if attr.get("type"):
                col_type = _strip_quotes(attr["type"])
                # Handle special Pydal types (id, reference)
                col_type = _process_pydal_type(col_type, attr)
                attr["type"] = col_type
    return data


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
            # Use existing table_name if set (e.g., from Pydal), otherwise derive it
            if not model.get("table_name"):
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
    # Clean up Pydal parsed data (strip quotes from names/types)
    if _is_pydal_result(result):
        result = _clean_pydal_data(result)
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
        header += generator.create_header(tables, models_str=models_str)
    else:
        header += enum.create_header(generator.enum_imports)
        models_type = "enum"
    output = render_jinja2_template(models_type, models_str, header)
    return output
