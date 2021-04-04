import os
from typing import Optional, List, Dict
from simple_ddl_parser import DDLParser, parse_from_file
from omymodels.gino import core as g
from omymodels.pydantic import core as p


def get_tables_information(
    ddl: Optional[str] = None, ddl_file: Optional[str] = None
) -> List[Dict]:
    if not ddl_file and not ddl:
        raise ValueError(
            "You need to provide one of above argument: ddl with string that "
            "contains ddl or ddl_file that contains path to ddl file to parse"
        )
    if ddl:
        tables = DDLParser(ddl).run()
    elif ddl_file:
        tables = parse_from_file(ddl_file)
    return tables


def create_models(
    ddl: Optional[str] = None,
    ddl_path: Optional[str] = None,
    dump: bool = True,
    dump_path: str = "models.py",
    singular: bool = False,
    naming_exceptions: Optional[List] = None,
    models_type: str = "gino",
):
    tables = get_tables_information(ddl, ddl_path)
    output = generate_models_file(tables, singular, naming_exceptions, models_type)
    if dump:
        save_models_to_file(output, dump_path)
    else:
        print(output)
    return {"metadata": tables, "code": output}


def save_models_to_file(models: str, dump_path: str) -> None:
    folder = os.path.dirname(dump_path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(dump_path, "w+") as f:
        f.write(models)


def generate_models_file(
    tables: List[Dict],
    singular: bool = False,
    exceptions: Optional[List] = None,
    models_type: str = "gino",
) -> str:
    """ method to prepare full file with all Models &  """
    output = ""

    models = {"gino": g, "pydantic": p}
    models_type = models.get(models_type)
    if not models_type:
        raise ValueError(
            f"Unsupported models type {models_type}. Possible variants: {models.keys()}"
        )

    model_generator = getattr(models_type, 'ModelGenerator')()
    
    for table in tables:
        output += model_generator.generate_model(table, singular, exceptions)
    header = model_generator.create_header(tables)
    output = header + output
    return output
