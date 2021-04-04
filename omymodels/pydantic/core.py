from typing import Optional, List, Dict
from omymodels.pydantic import templates as pt
from omymodels.utils import create_model_name
from omymodels.pydantic.types import types_mapping

imports = [pt.base_model]
types_for_import = ['Json']
datetime_import = True
typing_imports = []


def generate_attr(column: Dict) -> str:
    if column['nullable']:
        typing_imports.append('Optional')
        column_str = pt.pydantic_optional_attr
    else:
        column_str = pt.pydantic_attr
    _type = types_mapping.get(column['type'], "OMM_UNMAPPED_TYPE")
    if _type in types_for_import:
        imports.append(_type)
    elif 'datetime' in str(_type):
        datetime_import = True
    column_str = column_str.format(arg_name=column['name'], 
                                   type=_type)  
    
    return column_str
 
    
def generate_model(
    table: Dict, 
    singular: bool = False, 
    exceptions: Optional[List] = None) -> str:
    model = ""
    if table.get('table_name'):
        # mean one model one table
        model = pt.pydantic_class.format(
            class_name=create_model_name(
                table["table_name"], 
                singular, 
                exceptions), 
            table_name=table["table_name"]
        ) + '\n\n'
        for column in table["columns"]:
            model += generate_attr(column) + '\n'
    return model


def create_header(*args, **kwargs) -> str:
    header = ""
    if datetime_import:
        header += pt.datetime_import + "\n"
    if typing_imports:
        header += pt.typing_imports.format(typing_types=", ".join(typing_imports)) + "\n"
    header += pt.pydantic_imports.format(imports=', '.join(imports)) + '\n\n\n'
    return header

