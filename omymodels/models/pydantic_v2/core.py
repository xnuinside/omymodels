from typing import List, Optional

from table_meta.model import Column, TableMeta

import omymodels.types as t
from omymodels.helpers import create_class_name, datetime_now_check
from omymodels.models.pydantic_v2 import templates as pt
from omymodels.models.pydantic_v2.types import types_mapping
from omymodels.types import datetime_types, string_types

# Types that support max_length constraint
MAX_LENGTH_TYPES = string_types


class ModelGenerator:
    """Pydantic v2 model generator.

    Key differences from Pydantic v1:
    - Uses `X | None` syntax instead of `Optional[X]`
    - Uses `dict | list` for JSON types instead of `Json`
    - No need to import Json from pydantic
    """

    def __init__(self):
        self.imports = {pt.base_model}
        self.datetime_import = False
        self.typing_imports = set()
        self.custom_types = {}
        self.uuid_import = False
        self.prefix = ""

    def add_custom_type(self, target_type: str) -> Optional[str]:
        column_type = self.custom_types.get(target_type, None)
        _type = None
        if isinstance(column_type, tuple):
            _type = column_type[1]
        return _type

    def get_not_custom_type(self, column: Column) -> str:
        _type = None
        if "." in column.type:
            _type = column.type.split(".")[1]
        else:
            _type = column.type.lower().split("[")[0]
        _type = types_mapping.get(_type, _type)
        if "datetime" in _type:
            self.datetime_import = True
        elif "[" in column.type:
            # Array types use list[X] syntax in Python 3.9+
            _type = f"list[{_type}]"
        if _type == "UUID":
            self.uuid_import = True
        return _type

    def _should_add_max_length(self, column: Column) -> bool:
        """Check if column should have max_length constraint."""
        if not column.size:
            return False
        # Only add max_length for string types (varchar, char, etc.), not text
        original_type = column.type.lower().split("[")[0]
        return original_type in MAX_LENGTH_TYPES

    def generate_attr(self, column: Column, defaults_off: bool) -> str:
        _type = None
        max_length = column.size if self._should_add_max_length(column) else None

        # Pydantic v2 uses X | None syntax
        if column.nullable:
            column_str = pt.pydantic_nullable_attr
        else:
            column_str = pt.pydantic_attr

        if self.custom_types:
            _type = self.add_custom_type(column.type)
        if not _type:
            _type = self.get_not_custom_type(column)

        column_str = column_str.format(arg_name=column.name, type=_type)

        # Handle max_length with Field()
        if max_length is not None:
            self.imports.add("Field")
            field_params = []
            # Handle defaults
            if column.nullable and not defaults_off:
                field_params.append("default=None")
            elif column.default is not None and not defaults_off:
                default_val = self._get_default_value(column)
                if default_val:
                    field_params.append(f"default={default_val}")
            field_params.append(f"max_length={max_length}")
            column_str += f" = Field({', '.join(field_params)})"
        elif column.default is not None and not defaults_off:
            column_str = self.add_default_values(column_str, column)
        elif column.nullable and not defaults_off:
            # Nullable fields without explicit default should default to None
            column_str += pt.pydantic_default_attr.format(default="None")

        return column_str

    def _get_default_value(self, column: Column) -> str:
        """Get formatted default value for Field()."""
        if column.default is None or str(column.default).upper() == "NULL":
            return ""

        # Handle datetime default values
        if column.type.upper() in datetime_types:
            if datetime_now_check(column.default.lower()):
                return "datetime.datetime.now()"

        # Add quotes for string defaults if not already quoted
        default_val = column.default
        if isinstance(default_val, str) and "'" not in default_val and '"' not in default_val:
            default_val = f"'{default_val}'"
        return default_val

    @staticmethod
    def add_default_values(column_str: str, column: Column) -> str:
        # Handle datetime default values
        if column.type.upper() in datetime_types:
            if datetime_now_check(column.default.lower()):
                # Handle functions like CURRENT_TIMESTAMP
                column.default = "datetime.datetime.now()"
            elif column.default.upper() != "NULL" and "'" not in column.default:
                column.default = f"'{column.default}'"

        # If the default is 'NULL', set default to None for nullable fields
        if column.default.upper() == "NULL":
            column_str += pt.pydantic_default_attr.format(default="None")
            return column_str

        # Append the default value
        column_str += pt.pydantic_default_attr.format(default=column.default)
        return column_str

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
        ) + "\n\n"

        for column in table.columns:
            column = t.prepare_column_data(column)
            model += self.generate_attr(column, defaults_off) + "\n"

        return model

    def create_header(self, *args, **kwargs) -> str:
        header = ""
        # Required for X | None syntax in Python 3.9
        header += pt.future_annotations + "\n\n"
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
