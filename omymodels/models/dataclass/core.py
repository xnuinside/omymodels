from typing import Optional, List, Dict
from omymodels.models.dataclass import templates as dt
from omymodels.helpers import create_class_name
from omymodels.models.dataclass.types import types_mapping
from omymodels.types import datetime_types
import omymodels.types as t


class ModelGenerator:
    def __init__(self):

        self.types_for_import = ["Union"]
        self.datetime_import = False
        self.typing_imports = set()
        self.custom_types = {}
        self.uuid_import = False
        self.additional_imports = set()
        self.prefix = ""

    def add_custom_type(self, _type: str) -> str:
        column_type = self.custom_types.get(_type, _type)
        if isinstance(column_type, tuple):
            _type = column_type[1]
            column_type = column_type[0]
        return _type

    def generate_attr(self, column: Dict, defaults_off: bool) -> str:
        column_str = dt.dataclass_attr

        if "." in column.type:
            _type = column.type.split(".")[1]
        else:
            _type = column.type.lower().split("[")[0]
        if self.custom_types:
            _type = self.add_custom_type(_type)
        if _type == _type:
            _type = types_mapping.get(_type, _type)
        if _type.split("[")[0] in self.types_for_import:
            self.typing_imports.add(_type.split("[")[0])
        elif "datetime" in _type:
            self.datetime_import = True
            self.additional_imports.add("field")
        elif "[" in column.type:
            self.typing_imports.add("List")
            _type = f"List[{_type}]"
        if _type == "UUID":
            self.uuid_import = True
        column_str = column_str.format(arg_name=column.name, type=_type)
        if column.default and defaults_off is False:
            column_str = self.add_column_default(column_str, column)
        if (
            column.nullable
            and not (column.default and not defaults_off)
            and not defaults_off
        ):
            column_str += dt.dataclass_default_attr.format(default=None)
        return column_str

    @staticmethod
    def add_column_default(column_str: str, column: Dict) -> str:
        if column.type.upper() in datetime_types:
            if "now" in column.default.lower():
                # todo: need to add other popular PostgreSQL & MySQL functions
                column.default = dt.field_datetime_now
            elif "'" not in column.default:
                column.default = f"'{column['default']}'"
        column_str += dt.dataclass_default_attr.format(default=column.default)
        return column_str

    def generate_model(
        self,
        table: Dict,
        singular: bool = True,
        exceptions: Optional[List] = None,
        defaults_off: Optional[bool] = False,
        *args,
        **kwargs,
    ) -> str:
        model = ""

        # mean one model one table
        model += "\n\n"
        model += (
            dt.dataclass_class.format(
                class_name=create_class_name(table.name, singular, exceptions),
                table_name=table.name,
            )
        ) + "\n\n"
        columns = {"default": [], "non_default": []}
        for column in table.columns:
            column = t.prepare_column_data(column)
            column_str = self.generate_attr(column, defaults_off) + "\n"
            if "=" in column_str:
                columns["default"].append(column_str)
            else:
                columns["non_default"].append(column_str)
        for column in columns["non_default"]:
            model += column
        for column in columns["default"]:
            model += column
        return model

    def create_header(self, *args, **kwargs) -> str:
        header = ""
        if self.uuid_import:
            header += dt.uuid_import + "\n"
        if self.datetime_import:
            header += dt.datetime_import + "\n"
        if self.typing_imports:
            _imports = list(self.typing_imports)
            _imports.sort()
            header += dt.typing_imports.format(typing_types=", ".join(_imports)) + "\n"
        if self.additional_imports:
            self.additional_imports = f', {",".join(self.additional_imports)}'
        else:
            self.additional_imports = ""
        header += dt.dataclass_imports.format(
            additional_imports=self.additional_imports
        )
        return header
