from datetime import datetime
from keyword import iskeyword
from typing import List, Optional

from table_meta.model import Column, TableMeta

import omymodels.types as t
from omymodels.helpers import create_class_name, datetime_now_check
from omymodels.models.pydantic import templates as pt
from omymodels.models.pydantic.types import types_mapping
from omymodels.types import big_integer_types, integer_types, string_types, text_types


class ModelGenerator:
    def __init__(self):
        self.imports = {pt.base_model}
        self.types_for_import = []
        self.datetime_import = False
        self.date_import = False
        self.time_import = False
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

    def _handle_type_imports(self, _type: str, type_str: str) -> str:
        """Handle import tracking for the given type."""
        if _type in self.types_for_import:
            self.imports.add(_type)
        elif _type == "datetime":
            self.datetime_import = True
        elif _type == "date":
            self.date_import = True
        elif _type == "time":
            self.time_import = True
        elif "[" in type_str:
            self.typing_imports.add("List")
            _type = f"List[{_type}]"
        if _type == "UUID":
            self.uuid_import = True
        return _type

    def _normalize_type(self, _type: str) -> str:
        """Normalize type to Python equivalents."""
        type_lower = _type.lower()
        if any(t in type_lower for t in integer_types + big_integer_types):
            return "int"
        if any(t in type_lower for t in string_types + text_types):
            return "str"
        if type_lower == "any":
            self.typing_imports.add("Any")
            return "Any"
        return _type

    def get_not_custom_type(self, type_str: str) -> str:
        if "." in type_str:
            _type = type_str.split(".")[1]
        else:
            _type = type_str.lower().split("[")[0]

        _type = self.types_mapping.get(_type, _type)
        _type = self._handle_type_imports(_type, type_str)
        _type = self._normalize_type(_type)

        if "List" in _type:
            self.typing_imports.add("List")
        return _type

    def generate_attr(self, column: Column, defaults_off: bool) -> str:
        _type = None
        original_type = column.type  # Keep original for array detection

        if column.nullable:
            self.typing_imports.add("Optional")
            column_str = pt.pydantic_optional_attr
        else:
            column_str = pt.pydantic_attr

        if self.custom_types:
            _type = self.add_custom_type(column.type)
        if not _type:
            _type = t.prepare_type(column, self.types_mapping)
            _type = self.get_not_custom_type(_type)

        # Handle array types
        if "[" in original_type:
            self.typing_imports.add("List")
            _type = f"List[{_type}]"

        column.type = _type
        arg_name = column.name
        field_params = None

        # Check if we need Field() for alias or generated column
        generated_as = getattr(column, "generated_as", None)
        if not self._is_valid_identifier(column.name) or generated_as is not None:
            field_params = self._get_field_params(column, defaults_off)
            if field_params:
                self.imports.add("Field")
            arg_name = self._generate_valid_identifier(column.name)
        else:
            if column.default is not None and not defaults_off:
                field_params = self._get_default_value_string(column)

        column_str = column_str.format(
            arg_name=arg_name,
            type=_type,
            field_params=field_params if field_params is not None else "",
        )

        return column_str

    def _get_field_params(self, column: Column, defaults_off: bool) -> str:
        params = []

        if not self._is_valid_identifier(column.name):
            params.append(f'alias="{column.name}"')

        if column.default is not None and not defaults_off:
            if default_value := self._get_default_value_string(column):
                params.append(f"default{default_value.replace(' ', '')}")

        generated_as = getattr(column, "generated_as", None)
        if generated_as is not None:
            params.append("exclude=True")

        if params:
            return f" = Field({', '.join(params)})"
        return ""

    def _get_default_value_string(self, column: Column) -> str:
        if column.default is None or str(column.default).lower() == "null":
            return ""

        # Handle datetime default values
        if column.type.lower() in ["datetime", "timestamp"]:
            if datetime_now_check(str(column.default).lower()):
                self.datetime_import = True
                column.default = "datetime.now()"
            else:
                return pt.pydantic_default_attr.format(default=column.default)
        elif column.type.lower() == "date":
            self.date_import = True
            column.default = self._convert_to_date_string(str(column.default).strip("'"))
        elif column.type.lower() == "time":
            self.time_import = True
            column.default = self._convert_to_time_string(str(column.default).strip("'"))

        # Skip defaults for JSON types
        if column.type.lower() in ["any", "json", "jsonb"]:
            return ""

        # Handle numeric defaults (but not for array types)
        if "list[" not in column.type.lower() and any(
            t in column.type.lower() for t in list(integer_types) + list(big_integer_types)
        ):
            default_value = str(column.default).strip("'")
        elif column.type.lower() == "bool":
            # Convert 0/1 to False/True
            default_value = "False" if str(column.default).strip("'") == "0" else "True"
        else:
            default_value = column.default

        return pt.pydantic_default_attr.format(default=default_value)

    def _is_valid_identifier(self, name: str) -> bool:
        return (
            name.isidentifier()
            and not iskeyword(name)
            and not self._is_pydantic_reserved_name(name)
        )

    def _is_pydantic_reserved_name(self, name: str) -> bool:
        """Check if the name is a Pydantic-specific reserved name."""
        pydantic_reserved_prefixes = {"dict_", "json_"}
        pydantic_reserved_names = {
            "copy",
            "parse_obj",
            "parse_raw",
            "parse_file",
            "from_orm",
            "construct",
            "validate",
            "update_forward_refs",
            "schema",
            "schema_json",
            "register",
        }
        return (
            any(name.startswith(prefix) for prefix in pydantic_reserved_prefixes)
            or name in pydantic_reserved_names
        )

    def _generate_valid_identifier(self, name: str) -> str:
        """Generate a valid Python identifier from a given name."""
        valid_name = "".join(c if c.isalnum() else "_" for c in name)

        if (
            valid_name[0].isdigit()
            or iskeyword(valid_name)
            or self._is_pydantic_reserved_name(valid_name)
        ):
            valid_name = f"f_{valid_name}"

        return valid_name

    def _convert_to_date_string(self, date_str: str) -> str:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            return f"date({date_obj.year}, {date_obj.month}, {date_obj.day})"
        except ValueError:
            return date_str

    def _convert_to_time_string(self, time_str: str) -> str:
        try:
            time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
            return f"time({time_obj.hour}, {time_obj.minute}, {time_obj.second})"
        except ValueError:
            return time_str

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
        model += "\n\n"

        table_prefix = kwargs.get("table_prefix", "")
        table_suffix = kwargs.get("table_suffix", "")

        class_name = (
            table_prefix
            + create_class_name(table.name, singular, exceptions)
            + table_suffix
        )
        model += (
            pt.pydantic_class.format(
                class_name=class_name,
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
        if self.datetime_import or self.date_import or self.time_import:
            imports = []
            if self.datetime_import:
                imports.append("datetime")
            if self.date_import:
                imports.append("date")
            if self.time_import:
                imports.append("time")
            header += f"from datetime import {', '.join(imports)}\n"
        if self.typing_imports:
            _imports = list(self.typing_imports)
            _imports.sort()
            header += pt.typing_imports.format(typing_types=", ".join(_imports)) + "\n"
        self.imports = list(self.imports)
        self.imports.sort()
        header += pt.pydantic_imports.format(imports=", ".join(self.imports))
        return header
