from typing import Optional, List, Dict
from omymodels.pydantic import templates as pt
from omymodels.utils import create_model_name, type_not_found
from omymodels.pydantic.types import types_mapping


class ModelGenerator:
    
    def __init__(self):
        
        self.imports = set([pt.base_model])
        self.types_for_import = ["Json"]
        self.datetime_import = False
        self.typing_imports = set()

    def generate_attr(self, column: Dict) -> str:
        if column["nullable"]:
            self.typing_imports.add("Optional")
            column_str = pt.pydantic_optional_attr
        else:
            column_str = pt.pydantic_attr
        column_data_type = column["type"].lower().split("[")[0]
        _type = types_mapping.get(column_data_type, type_not_found)
        if _type in self.types_for_import:
            self.imports.add(_type)
        elif "datetime" in _type:
            self.datetime_import = True
        elif "[" in column["type"]:
            self.typing_imports.add("List")
            _type = f"List[{_type}]"
        column_str = column_str.format(arg_name=column["name"], type=_type)

        return column_str


    def generate_model(self,
        table: Dict, singular: bool = False, exceptions: Optional[List] = None
    ) -> str:
        model = ""
        if table.get("table_name"):
            # mean one model one table
            model += "\n\n"
            model += (
                pt.pydantic_class.format(
                    class_name=create_model_name(table["table_name"], singular, exceptions),
                    table_name=table["table_name"],
                )
                
            ) + "\n\n"
            for column in table["columns"]:
                model += self.generate_attr(column) + "\n"
        return model


    def create_header(self, *args, **kwargs) -> str:
        header = ""
        if self.datetime_import:
            header += pt.datetime_import + "\n"
        if self.typing_imports:
            _imports = list(self.typing_imports)
            _imports.sort()
            header += (
                pt.typing_imports.format(typing_types=", ".join(_imports)) + "\n"
            )
        header += pt.pydantic_imports.format(imports=", ".join(self.imports)) + "\n"
        return header
