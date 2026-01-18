"""Base generator for data model generators (Pydantic, Dataclass)."""

from typing import Any, Dict, List, Optional, Set

from table_meta.model import Column, TableMeta

from omymodels.generation.base import BaseGenerator
from omymodels.helpers import datetime_now_check
from omymodels.types import datetime_types


class DataModelGenerator(BaseGenerator):
    """Base class for data model generators (Pydantic, Dataclass).

    Provides common functionality for generating Python data classes
    and Pydantic models.
    """

    def __init__(self):
        super().__init__()
        self.datetime_import: bool = False
        self.uuid_import: bool = False
        self.typing_imports: Set[str] = set()
        self.types_for_import: List[str] = []

    def reset(self) -> None:
        """Reset generator state for reuse."""
        super().reset()
        self.datetime_import = False
        self.uuid_import = False
        self.typing_imports = set()

    def get_python_type(self, column: Column, types_mapping: Dict[str, str]) -> str:
        """Get Python type from SQL column type.

        Args:
            column: Column metadata
            types_mapping: Mapping of SQL types to Python types

        Returns:
            Python type as string
        """
        if "." in column.type:
            _type = column.type.split(".")[1]
        else:
            _type = column.type.lower().split("[")[0]

        # Check custom types first
        custom = self.get_custom_type(_type)
        if custom:
            return custom

        # Map to Python type
        _type = types_mapping.get(_type, _type)

        # Handle special types
        if _type in self.types_for_import:
            self.typing_imports.add(_type.split("[")[0])
        elif "datetime" in _type:
            self.datetime_import = True
        elif "[" in column.type:
            # Array type
            self.typing_imports.add("List")
            _type = f"List[{_type}]"

        if _type == "UUID":
            self.uuid_import = True

        return _type

    def format_default_value(self, column: Column, datetime_format: str) -> Optional[str]:
        """Format default value for Python.

        Args:
            column: Column with default value
            datetime_format: Format string for datetime.now() call

        Returns:
            Formatted default value or None
        """
        if column.default is None:
            return None

        default = column.default

        if isinstance(default, str):
            # Handle NULL default
            if default.upper() == "NULL":
                return "None"

            # Handle datetime defaults
            if column.type.upper() in datetime_types:
                if datetime_now_check(default.lower()):
                    return datetime_format
                elif "'" not in default:
                    return f"'{default}'"

            # Quote string defaults if needed
            if "'" not in default and not default.replace(".", "").replace("-", "").isdigit():
                return f"'{default}'"

        return str(default)

    def build_header_imports(
        self,
        uuid_template: str,
        datetime_template: str,
        typing_template: str,
    ) -> str:
        """Build common header imports.

        Args:
            uuid_template: Template for UUID import
            datetime_template: Template for datetime import
            typing_template: Template for typing imports (with {typing_types} placeholder)

        Returns:
            Import statements as string
        """
        header = ""

        if self.uuid_import:
            header += uuid_template + "\n"

        if self.datetime_import:
            header += datetime_template + "\n"

        if self.typing_imports:
            imports = sorted(self.typing_imports)
            header += typing_template.format(typing_types=", ".join(imports)) + "\n"

        return header
