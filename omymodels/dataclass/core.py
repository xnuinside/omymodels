from typing import Optional, List, Dict
from omymodels.dataclass import templates as pt
from omymodels.utils import create_class_name, type_not_found, enum_number_name_list
from omymodels.pydantic.types import types_mapping, datetime_types


class ModelGenerator:
    def __init__(self):

        self.imports = set([pt.base_model])
        self.types_for_import = ["Json"]
        self.datetime_import = False
        self.typing_imports = set()
        self.enum_imports = set()
        self.custom_types = {}
        self.uuid_import = False

    def generate_attr(self, column: Dict) -> str:
        column_str = pt.dataclass_attr
        
        if "." in column["type"]:
            _type = column["type"].split(".")[1]
        else:
            _type = column["type"].lower().split("[")[0]
        if self.custom_types:
            column_type = self.custom_types.get(_type, _type)
            if column_type != type_not_found:
                column_type = f"{column_type}({_type})"
        if _type == _type:
            _type = types_mapping.get(_type, _type)
        if _type in self.types_for_import:
            self.imports.add(_type)
        elif "datetime" in _type:
            self.datetime_import = True
        elif "[" in column["type"]:
            self.typing_imports.add("List")
            _type = f"List[{_type}]"
        if _type == 'UUID':
            self.uuid_import = True
        column_str = column_str.format(arg_name=column["name"], type=_type)
        if column["default"]:
            if column["type"].upper() in datetime_types:
                if "now" in column["default"]:
                    # todo: need to add other popular PostgreSQL & MySQL functions
                    column["default"] = "datetime.datetime.now()"
                elif "'" not in column["default"]:
                    column["default"] = f"'{column['default']}'"
            column_str += pt.dataclass_default_attr.format(default=column["default"])
        if column["nullable"]:
            column_str += pt.dataclass_default_attr.format(default=None)
        return column_str

    def generate_model(
        self, 
        table: Dict, 
        singular: bool = False, 
        exceptions: Optional[List] = None, 
        *args,
        **kwargs
    ) -> str:
        model = ""
        if table.get("table_name"):
            # mean one model one table
            model += "\n\n"
            model += (
                pt.dataclass_class.format(
                    class_name=create_class_name(
                        table["table_name"], singular, exceptions
                    ),
                    table_name=table["table_name"],
                )
            ) + "\n\n"
            columns = {'default': [], 'non_default': []}
            for column in table["columns"]:
                column_str = self.generate_attr(column) + "\n"
                if '=' in column_str:
                    columns['default'].append(column_str)
                else:
                    columns['non_default'].append(column_str)
            for column in columns['non_default']:
                model += column
            for column in columns['default']:
                model += column
        return model

    def create_header(self, *args, **kwargs) -> str:
        header = ""
        if self.enum_imports:
            header += pt.enum_import.format(enums=",".join(self.enum_imports)) + "\n"
        if self.uuid_import:
            header += pt.uuid_import + "\n"
        if self.datetime_import:
            header += pt.datetime_import + "\n"
        if self.typing_imports:
            _imports = list(self.typing_imports)
            _imports.sort()
            header += pt.typing_imports.format(typing_types=", ".join(_imports)) + "\n"
        header += pt.dataclass_imports + "\n"
        return header

    def generate_type(
        self, _type: Dict, singular: bool = False, exceptions: Optional[List] = None
    ) -> str:
        """ method to prepare one Model defention - name & tablename  & columns """
        type_class = ""
        if _type["properties"].get("values"):
            # mean this is a Enum
            _type["properties"]["values"].sort()
            for num, value in enumerate(_type["properties"]["values"]):
                _value = value.replace("'", "")
                if not _value.isnumeric():
                    type_class += (
                        pt.enum_value.format(name=value.replace("'", ""), value=value)
                        + "\n"
                    )
                    sub_type = 'str, Enum'
                    self.enum_imports.add("Enum")
                else:
                    type_class += (
                        pt.enum_value.format(
                            name=enum_number_name_list.get(num), value=_value
                        )
                        + "\n"
                    )
                    sub_type = 'IntEnum'
                    self.enum_imports.add("IntEnum")
            type_class = "\n\n" + (
            pt.enum_class.format(
                class_name=create_class_name(
                    _type["type_name"], singular, exceptions
                    
                ),
                sub_type=sub_type
            )
            + "\n\n"
        ) + type_class
            self.custom_types[_type["type_name"]] = "db.Enum"
        return type_class