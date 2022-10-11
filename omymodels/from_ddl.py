import os
import re
import sys
from typing import Dict, List, Optional

from simple_ddl_parser import DDLParser, parse_from_file
from table_meta import TableMeta, Type

from omymodels.errors import NoTablesError
from omymodels.generators import get_generator_by_type, render_jinja2_template
from omymodels.helpers import add_custom_types_to_generator
from omymodels.models.enum import core as enum


def get_tables_information(
    ddl: Optional[str] = None, ddl_file: Optional[str] = None
) -> List[Dict]:
    if not ddl_file and not ddl:
        raise ValueError(
            "You need to provide one of above argument: ddl with string that "
            "contains ddl or ddl_file that contains path to ddl file to parse"
        )
    if ddl:
        tables = DDLParser(ddl).run(group_by_type=True)
    elif ddl_file:
        tables = parse_from_file(ddl_file, group_by_type=True)
    return tables


def create_models(
    ddl: Optional[str] = None,
    ddl_path: Optional[str] = None,
    dump: bool = True,
    dump_path: str = "models.py",
    singular: bool = False,
    naming_exceptions: Optional[List] = None,
    models_type: str = "gino",
    schema_global: Optional[bool] = True,
    defaults_off: Optional[bool] = False,
    exit_silent: Optional[bool] = False,
    no_auto_snake_case: Optional[bool] = False
):
    """ models_type can be: "gino", "dataclass", "pydantic" """
    # extract data from ddl file
    data = get_tables_information(ddl, ddl_path)
    data = prepare_data(data)
    data = convert_ddl_to_models(data, no_auto_snake_case)
    if not data["tables"] and not data["types"]:
        if exit_silent:
            sys.exit(0)
        else:
            raise NoTablesError()
    # generate code
    output = generate_models_file(
        data, singular, naming_exceptions, models_type, schema_global, defaults_off
    )
    if dump:
        save_models_to_file(output, dump_path)
    else:
        print(output)
    return {"metadata": data, "code": output}


def snake_case(string: str) -> str:
    if string.lower() in ['id']:
        return string.lower()
    return re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()


def convert_ddl_to_models(data: Dict, no_auto_snake_case: bool) -> Dict[str, list]:
    final_data = {"tables": [], "types": []}
    tables = []
    for table in data["tables"]:
        for column in table["columns"]:
            if not no_auto_snake_case:
                column["name"] = snake_case(column["name"])
        tables.append(TableMeta(**table))
    final_data["tables"] = tables
    _types = []
    for _type in data["types"]:
        _types.append(Type(**_type))
    final_data["types"] = _types
    return final_data


def save_models_to_file(models: str, dump_path: str) -> None:
    folder = os.path.dirname(dump_path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(dump_path, "w+") as f:
        f.write(models)


def generate_models_file(
    data: Dict[str, List],
    singular: bool = False,
    exceptions: Optional[List] = None,
    models_type: str = "gino",
    schema_global: bool = True,
    defaults_off: Optional[bool] = False,
) -> str:
    """ method to prepare full file with all Models &  """
    models_str = ""
    generator = get_generator_by_type(models_type)
    header = ""
    if data["types"]:
        types_generator = enum.ModelGenerator(data["types"])
        models_str += types_generator.create_types()
        header += types_generator.create_header()
    if data["tables"]:

        add_custom_types_to_generator(data["types"], generator)

        for table in data["tables"]:
            models_str += generator.generate_model(
                table,
                singular,
                exceptions,
                schema_global=schema_global,
                defaults_off=defaults_off,
            )
        header += generator.create_header(data["tables"], schema=schema_global)
    else:
        models_type = "enum"
    output = render_jinja2_template(models_type, models_str, header)
    return output


def prepare_data(item: Dict) -> Dict:
    for key, value in item.items():
        if key.lower() != "default":
            if isinstance(value, list):
                value = iterate_over_the_list(value)
                item[key] = value
            elif isinstance(value, str) and key != "default":
                item[key] = clean_value(value)
            elif isinstance(value, dict):
                value = prepare_data(value)
    return item


def clean_value(string: str) -> str:
    string = string.replace('"', "")
    if string.startswith("[") and string.endswith("]"):
        string = string[1:-1]
    return string


def iterate_over_the_list(items: List) -> str:
    """ simple ddl parser return " in strings if in DDL them was used, we need to remove them"""
    for item in items:
        if isinstance(item, dict):
            prepare_data(item)
        elif isinstance(item, str):
            items.append(clean_value(item))
            items.remove(item)
    return items
