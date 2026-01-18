"""Base generator for ORM generators (Gino, SQLAlchemy, SQLModel)."""

from typing import Any, Dict, List, Optional, Set

from table_meta.model import Column

from omymodels.generation.base import BaseGenerator
from omymodels.helpers import datetime_now_check
from omymodels.types import datetime_types


class ORMGenerator(BaseGenerator):
    """Base class for ORM generators (Gino, SQLAlchemy, SQLModel).

    Provides common functionality for generating ORM models including
    column definitions, constraints, indexes, and foreign keys.
    """

    def __init__(self):
        super().__init__()
        self.state: Set[str] = set()
        self.postgresql_dialect_cols: Set[str] = set()
        self.constraint: bool = False
        self.im_index: bool = False
        self.types_mapping: Dict[str, str] = {}
        self.templates: Any = None

    def reset(self) -> None:
        """Reset generator state for reuse."""
        super().reset()
        self.state = set()
        self.postgresql_dialect_cols = set()
        self.constraint = False
        self.im_index = False

    def prepare_column_default(self, column: Column, column_str: str) -> str:
        """Process default value for ORM column.

        Handles datetime functions (NOW(), CURRENT_TIMESTAMP) and
        string quoting for server_default values.

        Args:
            column: Column metadata with default value
            column_str: Current column definition string

        Returns:
            Updated column string with default value
        """
        if column.default is None:
            return column_str

        default = column.default

        if isinstance(default, str):
            if column.type.upper() in datetime_types:
                if datetime_now_check(default.lower()):
                    default = "func.now()"
                    self.state.add("func")
                elif "'" not in default:
                    default = f"'{default}'"
            else:
                if "'" not in default:
                    default = f"'{default}'"
        else:
            default = f"'{str(default)}'"

        column_str += self.templates.default.format(default=default)
        return column_str

    def build_orm_header(
        self,
        tables: List,
        schema: bool,
        func_import: str,
        dialect_import: str,
        constraint_import: str,
        index_import: str,
    ) -> str:
        """Build common ORM header imports.

        Args:
            tables: List of tables
            schema: Whether schema is global
            func_import: Import for func (e.g., from sqlalchemy import func)
            dialect_import: Template for PostgreSQL dialect imports
            constraint_import: Import for UniqueConstraint
            index_import: Import for Index

        Returns:
            Header import statements
        """
        header = ""

        if "func" in self.state:
            header += func_import + "\n"

        if self.postgresql_dialect_cols:
            header += (
                dialect_import.format(types=",".join(self.postgresql_dialect_cols))
                + "\n"
            )

        if self.constraint:
            header += constraint_import + "\n"

        if self.im_index:
            header += index_import + "\n"

        return header
