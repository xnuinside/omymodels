import os
from typing import Optional, List, Dict
from simple_ddl_parser import DDLParser, parse_from_file
from omymodels.gino import core as g
from omymodels.pydantic import core as p
from omymodels.dataclass import core as d


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
    schema_global: Optional[bool] = True
):
    """
        models_type can be: "gino", "dataclass", "pydantic"
    
    """
    # extract data from ddl file
    data = get_tables_information(ddl, ddl_path)
    data = remove_quotes_from_strings(data)
    # generate code
    output = generate_models_file(data, singular, naming_exceptions, models_type, schema_global)
    if dump:
        save_models_to_file(output, dump_path)
    else:
        print(output)
    return {"metadata": data, "code": output}


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
    schema_global: bool = True
) -> str:
    """ method to prepare full file with all Models &  """
    output = ""
    models = {
        "gino": g, 
        "pydantic": p, 
        "dataclass": d
        }
    models_type = models.get(models_type)
    if not models_type:
        raise ValueError(
            f"Unsupported models type {models_type}. Possible variants: {models.keys()}"
        )
    model_generator = getattr(models_type, "ModelGenerator")()
    for _type in data["types"]:
        output += model_generator.generate_type(_type, singular, exceptions)
    for table in data["tables"]:
        output += model_generator.generate_model(table, singular, exceptions, schema_global)
    header = model_generator.create_header(data["tables"], schema=schema_global)
    output = header + output
    return output


def remove_quotes_from_strings(item: Dict) -> Dict:
    for key, value in item.items():
        if isinstance(value, list):
            value = iterate_over_the_list(value)
            item[key] = value
        elif isinstance(value, str) and key != 'default':
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
