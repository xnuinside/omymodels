from keyword import iskeyword
from typing import List, Optional

from table_meta.model import Column, TableMeta

import omymodels.types as t
from omymodels import types
from omymodels.helpers import create_class_name, datetime_now_check
from omymodels.models.pydantic import templates as pt
from omymodels.types import (
    big_integer_types,
    datetime_types,
    integer_types,
    string_types,
    text_types,
    types_mapping,
)


class ModelGenerator:
    def __init__(self):
        self.imports = {pt.base_model}
        self.types_for_import = ["Json"]
        self.datetime_import = False
        self.typing_imports = set()
        self.custom_types = {}
        self.uuid_import = False
        self.prefix = ""
        self.types_mapping = types_mapping

    def add_custom_type(self, target_type: str) -> Optional[str]:
        column_type = self.custom_types.get(target_type, None)
        _type = None
        if isinstance(column_type, tuple):
            _type = column_type[1]
        return _type

    def get_not_custom_type(self, type: str) -> str:
        _type = None
        if "." in type:
            _type = type.split(".")[1]
        else:
            _type = type.split("[")[0]
        _type = types_mapping.get(_type, _type)
        if _type in self.types_for_import:
            self.imports.add(_type)
        elif "datetime" in _type:
            self.datetime_import = True
        elif "[" in type:
            self.typing_imports.add("List")
            _type = f"List[{_type}]"
        if _type == "UUID":
            self.uuid_import = True
        # Handle integer types
        if any(t in _type for t in integer_types):
            _type = "int"
        # Handle big integer types
        if any(t in _type for t in big_integer_types):
            _type = "float"
        # Remove character set and collation information
        # Example: varchar(10) character set utf8mb4 collation utf8mb4_unicode_ci
        if any(t in _type for t in string_types + text_types):
            _type = "str"
        if "List" in _type:
            self.typing_imports.add("List")
        if "Any" == _type:
            self.typing_imports.add("Any")
        return _type

    def generate_attr(self, column: Column, defaults_off: bool) -> str:
        _type = None

        if column.nullable:
            self.typing_imports.add("Optional")
            column_str = pt.pydantic_optional_attr
        else:
            column_str = pt.pydantic_attr

        if self.custom_types:
            _type = self.add_custom_type(column.type)
        if not _type:
            _type = types.prepare_type(column, self.types_mapping)
            _type = self.get_not_custom_type(_type)

        arg_name = column.name
        field_params = None
        if not self._is_valid_identifier(column.name):
            field_params = self.get_field_params(column, defaults_off)
            if field_params:
                self.imports.add("Field")
            arg_name = self._generate_valid_identifier(column.name)
        else:
            if column.default is not None and not defaults_off:
                field_params = self.get_default_value_string(column)

        column_str = column_str.format(
            arg_name=arg_name,
            type=_type,
            field_params=field_params if field_params is not None else "",
        )

        return column_str

    def get_field_params(self, column: Column, defaults_off: bool) -> str:
        params = []

        if not self._is_valid_identifier(column.name):
            params.append(f'alias="{column.name}"')

        if not any(t in column.type.lower() for t in ["json", "jsonb"]):
            if column.default is not None and not defaults_off:
                default_value = self.get_default_value(column)
                if default_value:
                    if any(
                        t in column.type.lower()
                        for t in integer_types + big_integer_types
                    ):
                        # Remove quotes for integer types
                        default_value = default_value.strip("'")
                        params.append(f"default={default_value}")
                    else:
                        # Keep quotes for other types
                        params.append(f"default={default_value}")

        if params:
            return f" = Field({', '.join(params)})"
        return ""

    def get_default_value(self, column: Column) -> str:
        if column.default is None or column.default.lower() == "null":
            return ""

        if column.type.lower() in datetime_types:
            if datetime_now_check(column.default.lower()):
                self.datetime_import = True
                return "datetime.now()"
            else:
                return column.default.strip("'")

        return column.default

    @staticmethod
    def _is_valid_identifier(name: str) -> bool:
        """Check if the given name is a valid Python identifier."""
        return name.isidentifier() and not iskeyword(name)

    @staticmethod
    def _generate_valid_identifier(name: str) -> str:
        """Generate a valid Python identifier from a given name."""
        # Replace non-alphanumeric characters with underscores
        valid_name = "".join(c if c.isalnum() else "_" for c in name)
        # Ensure the name doesn't start with a number
        if valid_name[0].isdigit():
            valid_name = f"f_{valid_name}"
        # Ensure it's not a Python keyword
        if iskeyword(valid_name):
            valid_name += "_"
        return valid_name

    @staticmethod
    def get_default_value_string(column: Column) -> str:
        # Handle datetime default values
        if column.type.lower() in datetime_types:
            if datetime_now_check(column.default.lower()):
                column.default = "datetime.now()"
            elif column.default.lower() != "null" and "'" not in column.default:
                column.default = f"'{column.default}'"

        # If the default is 'NULL', don't set a default in Pydantic (it already defaults to None)
        if column.default.lower() == "null":
            return ""
        if any(t in column.type.lower() for t in ["json", "jsonb"]):
            return ""
        # Remove quotes for integer types
        if any(t in column.type.lower() for t in integer_types + big_integer_types):
            default_value = column.default.strip("'")
        else:
            default_value = column.default

        # Append the default value if it's not None (e.g., explicit default values like '0' or CURRENT_TIMESTAMP)
        return pt.pydantic_default_attr.format(default=default_value)

    def generate_model(
        self,
        table: TableMeta,
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
            pt.pydantic_class.format(
                class_name=create_class_name(table.name, singular, exceptions),
                table_name=table.name,
            )
        ) + "\n"

        for column in table.columns:
            column = t.prepare_column_data(column)
            model += self.generate_attr(column, defaults_off) + "\n"

        return model

    def create_header(self, *args, **kwargs) -> str:
        header = ""
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
