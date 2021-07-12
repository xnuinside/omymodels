import os
import pathlib
import sys
from jinja2 import Template

from typing import Optional, List, Dict

from simple_ddl_parser import DDLParser, parse_from_file
from omymodels.gino import core as g
from omymodels.pydantic import core as p
from omymodels.dataclass import core as d
from omymodels.sqlalchemy import core as s
from omymodels.sqlalchemy_core import core as sc
from omymodels.meta_model import TableMeta, Type


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
):
    """ models_type can be: "gino", "dataclass", "pydantic" """
    # extract data from ddl file
    data = get_tables_information(ddl, ddl_path)
    data = remove_quotes_from_strings(data)
    data = convert_ddl_to_models(data)
    if not data["tables"]:
        sys.exit(0)
    # generate code
    output = generate_models_file(
        data, singular, naming_exceptions, models_type, schema_global, defaults_off
    )
    if dump:
        save_models_to_file(output, dump_path)
    else:
        print(output)
    return {"metadata": data, "code": output}


def convert_ddl_to_models(data):
    final_data = {"tables": [], "types": []}
    tables = []
    for table in data["tables"]:
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
    models = {
        "gino": g,
        "pydantic": p,
        "dataclass": d,
        "sqlalchemy": s,
        "sqlalchemy_core": sc,
    }
    model = models.get(models_type)
    if not model:
        raise ValueError(
            f"Unsupported models type {models_type}. Possible variants: {models.keys()}"
        )
    model_generator = getattr(model, "ModelGenerator")()
    for _type in data["types"]:
        models_str += model_generator.generate_type(_type, singular, exceptions)
    for table in data["tables"]:
        models_str += model_generator.generate_model(
            table,
            singular,
            exceptions,
            schema_global=schema_global,
            defaults_off=defaults_off,
        )
    header = model_generator.create_header(data["tables"], schema=schema_global)
    output = render_jinja2_template(models_type, models_str, header)
    return output


def render_jinja2_template(models_type: str, models: str, headers: str) -> str:
    template_file = (
        pathlib.Path(__file__).parent / models_type / f"{models_type}.jinja2"
    )

    with open(template_file) as t:
        template = t.read()
        template = Template(template)
        params = {"models": models, "headers": headers}
        return template.render(**params)


def remove_quotes_from_strings(item: Dict) -> Dict:
    for key, value in item.items():
        if key.lower() != "default":
            if isinstance(value, list):
                value = iterate_over_the_list(value)
                item[key] = value
            elif isinstance(value, str) and key != "default":
                item[key] = value.replace('"', "")
            elif isinstance(value, dict):
                value = remove_quotes_from_strings(value)
    return item


def iterate_over_the_list(items: List) -> str:
    """ simple ddl parser return " in strings if in DDL them was used, we need to remove them"""
    for item in items:
        if isinstance(item, dict):
            remove_quotes_from_strings(item)
        elif isinstance(item, str):
            new_item = item.replace('"', "")
            items.remove(item)
            items.append(new_item)
    return items
