from typing import Optional, List, Dict
from omymodels.pydantic import templates as pt
from omymodels.utils import create_class_name, enum_number_name_list
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

    def add_custom_type(self, _type):
        column_type = self.custom_types.get(_type, _type)
        if isinstance(column_type, tuple):
            _type = column_type[1]
            column_type = column_type[0]
        return _type

    def generate_attr(self, column: Dict, defaults_off: bool) -> str:
        if column.nullable:
            self.typing_imports.add("Optional")
            column_str = pt.pydantic_optional_attr
        else:
            column_str = pt.pydantic_attr
        if "." in column.type:
            _type = column.type.split(".")[1]
        else:
            _type = column.type.lower().split("[")[0]
        if self.custom_types:
            _type = self.add_custom_type(_type)
        if _type == _type:
            _type = types_mapping.get(_type, _type)
        if _type in self.types_for_import:
            self.imports.add(_type)
        elif "datetime" in _type:
            self.datetime_import = True
        elif "[" in column.type:
            self.typing_imports.add("List")
            _type = f"List[{_type}]"
        if _type == "UUID":
            self.uuid_import = True

        column_str = column_str.format(arg_name=column.name, type=_type)

        if column.default and defaults_off is False:
            column_str = self.add_default_values(column_str, column)

        return column_str

    @staticmethod
    def add_default_values(column_str: str, column: Dict) -> str:
        if column.type.upper() in datetime_types:
            if "now" in column.default.lower():
                # todo: need to add other popular PostgreSQL & MySQL functions
                column.default = "datetime.datetime.now()"
            elif "'" not in column.default:
                column.default = f"'{column['default']}'"
        column_str += pt.pydantic_default_attr.format(default=column.default)
        return column_str

    def generate_model(
        self,
        table: Dict,
        singular: bool = False,
        exceptions: Optional[List] = None,
        defaults_off: Optional[bool] = False,
        *args,
        **kwargs,
    ) -> str:
        model = ""
        # mean one model one table
        model += "\n\n"
        model += (
            pt.pydantic_class.format(
                class_name=create_class_name(table.name, singular, exceptions),
                table_name=table.name,
            )
        ) + "\n\n"

        for column in table.columns:
            model += self.generate_attr(column, defaults_off) + "\n"

        return model

    def create_header(self, *args, **kwargs) -> str:
        header = ""
        if self.enum_imports:
            self.enum_imports = list(self.enum_imports)
            self.enum_imports.sort()
            header += pt.enum_import.format(enums=", ".join(self.enum_imports)) + "\n"
        if self.uuid_import:
            header += pt.uuid_import + "\n"
        if self.datetime_import:
            header += pt.datetime_import + "\n"
        if self.typing_imports:
            _imports = list(self.typing_imports)
            _imports.sort()
            header += pt.typing_imports.format(typing_types=", ".join(_imports)) + "\n"
        self.imports = list(self.imports)
        self.imports.sort()
        header += pt.pydantic_imports.format(imports=", ".join(self.imports))
        return header

    def generate_type(
        self, _type: Dict, singular: bool = False, exceptions: Optional[List] = None
    ) -> str:
        """ method to prepare one Model defention - name & tablename & columns """
        type_class = ""
        if _type.properties.get("values"):
            # mean this is a Enum
            _type.properties["values"].sort()
            for num, value in enumerate(_type.properties["values"]):
                _value = value.replace("'", "")
                if not _value.isnumeric():
                    type_class += (
                        pt.enum_value.format(name=value.replace("'", ""), value=value)
                        + "\n"
                    )
                    sub_type = "str, Enum"
                    self.enum_imports.add("Enum")
                else:
                    type_class += (
                        pt.enum_value.format(
                            name=enum_number_name_list.get(num), value=_value
                        )
                        + "\n"
                    )
                    sub_type = "IntEnum"
                    self.enum_imports.add("IntEnum")
            class_name = create_class_name(_type.name, singular, exceptions)
            type_class = (
                "\n\n"
                + (
                    pt.enum_class.format(class_name=class_name, sub_type=sub_type)
                    + "\n\n"
                )
                + type_class
            )
            self.custom_types[_type.name] = ("db.Enum", class_name)
        return type_class
