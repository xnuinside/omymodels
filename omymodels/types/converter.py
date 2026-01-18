"""Type converter for SQL to target framework types."""

from typing import Dict, Optional, Tuple, Union

from omymodels.types.sql_types import datetime_types, json_types


class TypeConverter:
    """Converter for SQL types to target framework types.

    Provides a unified interface for converting SQL column types
    to the appropriate types for different frameworks (ORM, Pydantic, etc.).
    """

    def __init__(self, mapping: Dict[str, str], prefix: str = ""):
        """Initialize type converter.

        Args:
            mapping: Dictionary mapping SQL types to target types
            prefix: Prefix to add to types (e.g., "db." for Gino)
        """
        self.mapping = mapping
        self.prefix = prefix
        self._lookup: Dict[str, str] = {}
        self._build_lookup()

    def _build_lookup(self) -> None:
        """Build lowercase lookup table for fast type resolution."""
        self._lookup = {}
        for sql_type, target_type in self.mapping.items():
            self._lookup[sql_type.lower()] = target_type

    def convert(self, sql_type: str) -> str:
        """Convert SQL type to target type.

        Args:
            sql_type: SQL column type (e.g., "VARCHAR(100)", "INTEGER")

        Returns:
            Target framework type
        """
        # Normalize: lowercase and remove size specifier
        normalized = sql_type.lower().split("(")[0].split("[")[0].strip()
        return self._lookup.get(normalized, sql_type)

    def with_size(
        self, type_str: str, size: Optional[Union[int, Tuple[int, ...]]]
    ) -> str:
        """Add size specification to type.

        Args:
            type_str: Base type string
            size: Size as int or tuple (for precision/scale)

        Returns:
            Type string with size
        """
        if size is None:
            return type_str

        if isinstance(size, tuple):
            size_str = ", ".join(str(s) for s in size)
            return f"{type_str}({size_str})"

        return f"{type_str}({size})"

    def is_datetime(self, sql_type: str) -> bool:
        """Check if SQL type is a datetime type.

        Args:
            sql_type: SQL column type

        Returns:
            True if datetime type
        """
        return sql_type.upper() in datetime_types

    def is_json(self, sql_type: str) -> bool:
        """Check if SQL type is a JSON type.

        Args:
            sql_type: SQL column type

        Returns:
            True if JSON type
        """
        return sql_type.lower() in json_types

    def update(self, mapping: Dict[str, str]) -> None:
        """Update type mapping with additional types.

        Args:
            mapping: Additional type mappings to add
        """
        self.mapping.update(mapping)
        self._build_lookup()

    def get(self, sql_type: str, default: Optional[str] = None) -> Optional[str]:
        """Get target type for SQL type.

        Args:
            sql_type: SQL column type
            default: Default value if type not found

        Returns:
            Target type or default
        """
        normalized = sql_type.lower().split("(")[0].strip()
        return self._lookup.get(normalized, default)
