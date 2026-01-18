"""Base generator class for all model generators."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from table_meta.model import TableMeta


class BaseGenerator(ABC):
    """Abstract base class for all model generators.

    All generators (ORM, Pydantic, Dataclass, etc.) should inherit from this class
    and implement the abstract methods.
    """

    def __init__(self):
        self.custom_types: Dict[str, Any] = {}
        self.prefix: str = ""

    @abstractmethod
    def generate_model(
        self,
        table: TableMeta,
        singular: bool = True,
        exceptions: Optional[List[str]] = None,
        **kwargs,
    ) -> str:
        """Generate code for a single model.

        Args:
            table: TableMeta object with table information
            singular: Whether to singularize table name for class name
            exceptions: List of words to exclude from singularization
            **kwargs: Additional generator-specific options

        Returns:
            Generated model code as string
        """
        pass

    @abstractmethod
    def create_header(self, tables: List[TableMeta], **kwargs) -> str:
        """Generate file header with imports.

        Args:
            tables: List of all tables (for determining required imports)
            **kwargs: Additional generator-specific options

        Returns:
            Generated header code as string
        """
        pass

    def add_custom_type(self, type_name: str, type_def: Any) -> None:
        """Register a custom type (e.g., enum).

        Args:
            type_name: Name of the custom type
            type_def: Type definition (can be tuple of (original, mapped))
        """
        self.custom_types[type_name] = type_def

    def get_custom_type(self, type_name: str) -> Optional[str]:
        """Get mapped custom type if exists.

        Args:
            type_name: Name of the type to look up

        Returns:
            Mapped type name or None if not found
        """
        column_type = self.custom_types.get(type_name)
        if isinstance(column_type, tuple):
            return column_type[1]
        return None

    def reset(self) -> None:
        """Reset generator state for reuse."""
        self.custom_types = {}
