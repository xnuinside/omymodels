import copy
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
        tables = DDLParser(ddl, normalize_names=True).run(group_by_type=True)
    elif ddl_file:
        tables = parse_from_file(
            ddl_file, parser_settings={"normalize_names": True}, group_by_type=True
        )
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
    no_auto_snake_case: Optional[bool] = False,
    table_prefix: Optional[str] = "",
    table_suffix: Optional[str] = "",
    relationships: Optional[bool] = False,
):
    """models_type can be: "gino", "dataclass", "pydantic" """
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
        data,
        singular,
        naming_exceptions,
        models_type,
        schema_global,
        defaults_off,
        table_prefix=table_prefix,
        table_suffix=table_suffix,
        relationships=relationships,
    )
    if dump:
        save_models_to_file(output, dump_path)
    else:
        print(output)
    return {"metadata": data, "code": output}


def snake_case(string: str) -> str:
    if string.lower() in ["id"]:
        return string.lower()
    return re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()


def convert_ddl_to_models(  # noqa: C901
    data: Dict, no_auto_snake_case: bool
) -> Dict[str, list]:
    final_data = {"tables": [], "types": []}
    refs = {}
    tables = []
    for table in data["tables"]:
        for ref in table.get("constraints", {}).get("references", []):
            # References can be compopund references.  Here we split into one
            # reference per column and then attach it to the column in the next
            # loop.
            for i in range(len(ref["columns"])):
                ref_name = (
                    ref["name"].split(",")[i]
                    if isinstance(ref["name"], str)
                    else ref["name"][i]
                )
                if not no_auto_snake_case:
                    ref_name = snake_case(ref_name)
                single_ref = copy.deepcopy(ref)
                single_ref["column"] = ref["columns"][i]
                del single_ref["columns"]
                ref_name = ref_name.replace('"', "")
                refs[ref_name] = single_ref
        for column in table["columns"]:
            if not no_auto_snake_case:
                column["name"] = snake_case(column["name"])
            if column["name"] in refs:
                column["references"] = refs[column["name"]]
            # Handle generated columns (GENERATED ALWAYS AS)
            if "generated" in column:
                column["generated_as"] = column["generated"].get("as")
        if not no_auto_snake_case:
            table["primary_key"] = [snake_case(pk) for pk in table["primary_key"]]
            for uniq in table.get("constraints", {}).get("uniques", []):
                uniq["columns"] = [snake_case(c) for c in uniq["columns"]]
            # NOTE: We are not going to try and parse check constraint statements
            # and update the snake case.
            for idx in table.get("index", []):
                idx["columns"] = [snake_case(c) for c in idx["columns"]]
                for col_detail in idx["detailed_columns"]:
                    col_detail["name"] = snake_case(col_detail["name"])
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


def collect_relationships(tables: List) -> Dict:
    """Collect foreign key relationships between tables.

    Returns a dict mapping table_name -> list of relationships info.
    Each relationship has:
    - fk_column: the foreign key column name in the child table
    - ref_table: the referenced (parent) table name
    - ref_column: the referenced column name

    Checks both inline column references and ALTER TABLE foreign keys.
    """
    relationships = {}

    def add_relationship(table_name: str, fk_column: str, ref_table: str, ref_column: str):
        """Helper to add both sides of a relationship."""
        # Add to child table's relationships (many-to-one)
        if table_name not in relationships:
            relationships[table_name] = []
        relationships[table_name].append({
            "type": "many_to_one",
            "fk_column": fk_column,
            "ref_table": ref_table,
            "ref_column": ref_column,
            "child_table_name": table_name,  # The child needs to know its own table name for back_populates
        })
        # Add to parent table's relationships (one-to-many)
        if ref_table not in relationships:
            relationships[ref_table] = []
        relationships[ref_table].append({
            "type": "one_to_many",
            "child_table": table_name,
            "fk_column": fk_column,
        })

    for table in tables:
        # Check inline column references
        for column in table.columns:
            if column.references:
                ref_table = column.references.get("table")
                ref_column = column.references.get("column") or column.name
                if ref_table:
                    add_relationship(table.name, column.name, ref_table, ref_column)

        # Check ALTER TABLE foreign keys
        if hasattr(table, 'alter') and table.alter and "columns" in table.alter:
            for alter_column in table.alter["columns"]:
                if alter_column.get("references"):
                    ref_info = alter_column["references"]
                    ref_table = ref_info.get("table")
                    ref_column = ref_info.get("column") or alter_column["name"]
                    if ref_table:
                        add_relationship(table.name, alter_column["name"], ref_table, ref_column)

    return relationships


def generate_models_file(
    data: Dict[str, List],
    singular: bool = False,
    exceptions: Optional[List] = None,
    models_type: str = "gino",
    schema_global: bool = True,
    defaults_off: Optional[bool] = False,
    table_prefix: Optional[str] = "",
    table_suffix: Optional[str] = "",
    relationships: Optional[bool] = False,
) -> str:
    """method to prepare full file with all Models &"""
    models_str = ""
    generator = get_generator_by_type(models_type)
    header = ""
    if data["types"]:
        types_generator = enum.ModelGenerator(data["types"])
        models_str += types_generator.create_types()
        header += types_generator.create_header()
    if data["tables"]:
        add_custom_types_to_generator(data["types"], generator)

        # Collect relationships if enabled
        relationships_map = {}
        if relationships:
            relationships_map = collect_relationships(data["tables"])

        for table in data["tables"]:
            models_str += generator.generate_model(
                table,
                singular,
                exceptions,
                schema_global=schema_global,
                defaults_off=defaults_off,
                table_prefix=table_prefix,
                table_suffix=table_suffix,
                relationships=relationships_map.get(table.name, []) if relationships else [],
            )
        header += generator.create_header(
            data["tables"], schema=schema_global, models_str=models_str
        )
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
        else:
            item[key] = format_to_py_var(value)
    return item


def format_to_py_var(value: str) -> str:
    if value in ["false", "true"]:
        return value.capitalize()
    return value


def clean_value(string: str) -> str:
    string = string.replace('"', "")
    if string.startswith("[") and string.endswith("]"):
        string = string[1:-1]
    return string


def iterate_over_the_list(items: List) -> List:
    """Clean list items - remove quotes from strings and process dicts.

    simple-ddl-parser returns quotes in strings if DDL used them.
    """
    return [
        clean_value(item) if isinstance(item, str)
        else prepare_data(item) if isinstance(item, dict)
        else item
        for item in items
    ]
