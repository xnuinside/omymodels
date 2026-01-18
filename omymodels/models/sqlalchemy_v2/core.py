from typing import Dict, List, Optional

import omymodels.models.sqlalchemy_v2.templates as st
from omymodels.helpers import create_class_name, datetime_now_check
from omymodels.models.sqlalchemy_v2.types import types_mapping, python_to_sa_type
from omymodels.types import datetime_types, json_types, postgresql_dialect
import omymodels.types as t


class GeneratorBase:
    def __init__(self):
        self.custom_types = {}


class ModelGenerator(GeneratorBase):
    def __init__(self):
        self.state = set()
        self.postgresql_dialect_cols = set()
        self.typing_imports = set()
        self.constraint = False
        self.im_index = False
        self.datetime_import = False
        self.date_import = False
        self.time_import = False
        self.uuid_import = False
        self.fk_import = False
        self.relationship_import = False
        self.types_mapping = types_mapping
        self.templates = st
        self.prefix = ""
        super().__init__()

    def prepare_column_default(self, column_data: Dict, column: str) -> str:
        if isinstance(column_data.default, str):
            if column_data.type.upper() in datetime_types:
                if datetime_now_check(column_data.default.lower()):
                    column_data.default = "func.now()"
                    self.state.add("func")
                elif "'" not in column_data.default:
                    column_data.default = f"'{column_data.default}'"
            else:
                if "'" not in column_data.default:
                    column_data.default = f"'{column_data.default}'"
        else:
            column_data.default = f"'{str(column_data.default)}'"
        column += st.default.format(default=column_data.default)
        return column

    def _get_python_type(self, column_type_info) -> str:
        """Get Python type for Mapped annotation."""
        if isinstance(column_type_info, dict):
            return column_type_info.get("python", "str")
        return column_type_info

    def _get_sa_type(self, column_type_info) -> str:
        """Get SQLAlchemy column type."""
        if isinstance(column_type_info, dict):
            return column_type_info.get("sa")
        return None

    def _track_imports(self, python_type: str):
        """Track necessary imports based on Python type."""
        if python_type == "datetime":
            self.datetime_import = True
        elif python_type == "date":
            self.date_import = True
        elif python_type == "time":
            self.time_import = True
        elif python_type == "UUID":
            self.uuid_import = True

    def _resolve_type_info(self, column_data) -> tuple:
        """Resolve Python and SQLAlchemy types for a column."""
        column_type_info = self.types_mapping.get(
            column_data.type.lower().split("[")[0],
            {"python": "str", "sa": "String"}
        )

        python_type = self._get_python_type(column_type_info)
        sa_type = self._get_sa_type(column_type_info)

        # Handle custom types (enums)
        if self.custom_types:
            custom = self.custom_types.get(column_data.type)
            if custom:
                if isinstance(custom, tuple):
                    python_type = custom[1]
                    sa_type = f"Enum({custom[1]})"
                else:
                    python_type = column_data.type
                    sa_type = f"Enum({column_data.type})"

        return python_type, sa_type

    def _handle_array_type(self, column_data, python_type, sa_type) -> tuple:
        """Handle array type columns."""
        if "[" in column_data.type and column_data.type.lower() not in json_types:
            self.postgresql_dialect_cols.add("ARRAY")
            self.typing_imports.add("List")
            array_sa_type = python_to_sa_type.get(python_type, "String")
            sa_type = f"ARRAY({array_sa_type})"
            python_type = f"List[{python_type}]"
        return python_type, sa_type

    def _add_type_size(self, sa_type, column_data) -> str:
        """Add size specification to SQLAlchemy type."""
        if sa_type and column_data.size:
            if isinstance(column_data.size, int):
                return f"{sa_type}({column_data.size})"
            elif isinstance(column_data.size, tuple):
                return f"{sa_type}({','.join(str(x) for x in column_data.size)})"
        return sa_type

    def generate_column(
        self,
        column_data,
        table_pk: List[str],
        table_data: Dict,
        schema_global: bool,
    ) -> str:
        """Generate a column definition in SQLAlchemy 2.0 style."""
        column_data = t.prepare_column_data(column_data)

        python_type, sa_type = self._resolve_type_info(column_data)
        self._track_imports(python_type)

        python_type, sa_type = self._handle_array_type(column_data, python_type, sa_type)

        if column_data.nullable and column_data.name not in table_pk:
            python_type = f"{python_type} | None"

        if sa_type and sa_type in postgresql_dialect:
            self.postgresql_dialect_cols.add(sa_type)

        sa_type_with_size = self._add_type_size(sa_type, column_data)

        if sa_type_with_size:
            column = st.column_template.format(
                column_name=column_data.name,
                python_type=python_type,
                column_type=sa_type_with_size,
            )
        else:
            column = st.column_template_no_type.format(
                column_name=column_data.name,
                python_type=python_type,
            )

        column = self._add_column_attributes(
            column, column_data, table_pk, table_data, schema_global
        )

        column += ")\n"
        return column

    def _add_column_attributes(
        self,
        column: str,
        column_data,
        table_pk: List[str],
        table_data: Dict,
        schema_global: bool,
    ) -> str:
        """Add attributes to column definition."""
        # Handle foreign keys from ALTER statements
        if "columns" in table_data.alter:
            for alter_column in table_data.alter["columns"]:
                if (
                    alter_column["name"] == column_data.name
                    and not alter_column["constraint_name"]
                    and alter_column["references"]
                ):
                    column = self._add_foreign_key(
                        column, alter_column["references"], schema_global
                    )

        # Handle autoincrement
        if column_data.type.lower() in ("serial", "bigserial"):
            column += st.autoincrement

        # Handle inline foreign keys
        if column_data.references:
            column = self._add_foreign_key(
                column, column_data.references, schema_global
            )

        # Handle default values
        if column_data.default is not None:
            column = self.prepare_column_default(column_data, column)

        # Handle primary key
        if column_data.name in table_pk:
            column += st.pk_template

        # Handle unique constraint
        if column_data.unique:
            column += st.unique

        return column

    def _add_foreign_key(
        self, column: str, reference: Dict[str, str], schema_global: bool
    ) -> str:
        """Add foreign key to column definition."""
        self.fk_import = True
        if reference["schema"] and not schema_global:
            column += st.fk_in_column.format(
                ref_schema=reference["schema"],
                ref_table=reference["table"],
                ref_column=reference["column"] or column,
            )
        else:
            column += st.fk_in_column_without_schema.format(
                ref_table=reference["table"],
                ref_column=reference["column"] or column,
            )
        if reference["on_delete"]:
            column += st.on_delete.format(mode=reference["on_delete"].upper())
        if reference["on_update"]:
            column += st.on_update.format(mode=reference["on_update"].upper())
        return column

    def generate_model(
        self,
        table: Dict,
        singular: bool = True,
        exceptions: Optional[List] = None,
        schema_global: Optional[bool] = True,
        relationships: Optional[List] = None,
        *args,
        **kwargs,
    ) -> str:
        """Generate a model definition in SQLAlchemy 2.0 style."""
        model = st.model_template.format(
            model_name=create_class_name(table.name, singular, exceptions),
            table_name=table.name,
        )

        for column in table.columns:
            model += self.generate_column(
                column, table.primary_key, table, schema_global
            )

        if table.indexes or table.alter or table.checks or not schema_global:
            model = self._add_table_args(model, table, schema_global)

        # Generate relationships if enabled
        if relationships:
            model += self._generate_relationships(
                relationships, singular, exceptions
            )

        return model

    def _generate_relationships(
        self,
        relationships: List[Dict],
        singular: bool,
        exceptions: Optional[List] = None,
    ) -> str:
        """Generate relationship() lines for the model."""
        result = "\n"
        self.relationship_import = True
        self.typing_imports.add("List")

        for rel in relationships:
            if rel["type"] == "many_to_one":
                # Child side: reference to parent
                # e.g., author: Mapped["Authors"] = relationship("Authors", back_populates="books")
                ref_table = rel["ref_table"]
                fk_column = rel["fk_column"]
                child_table_name = rel["child_table_name"]
                related_class = create_class_name(ref_table, singular, exceptions)
                # Attribute name derived from FK column (author_id -> author)
                attr_name = fk_column.replace("_id", "") if fk_column.endswith("_id") else ref_table.lower()
                # back_populates points to the collection on the parent (uses child table name)
                back_pop_name = child_table_name.lower().replace("-", "_")
                back_populates = st.back_populates_template.format(attr_name=back_pop_name)
                # Type hint for many-to-one is the related class (quoted for forward ref)
                type_hint = f'"{related_class}"'
                result += st.relationship_template.format(
                    attr_name=attr_name,
                    type_hint=type_hint,
                    related_class=related_class,
                    back_populates=back_populates,
                )
            elif rel["type"] == "one_to_many":
                # Parent side: collection of children
                # e.g., books: Mapped[List["Books"]] = relationship("Books", back_populates="author")
                child_table = rel["child_table"]
                fk_column = rel["fk_column"]
                related_class = create_class_name(child_table, singular, exceptions)
                # Attribute name is the child table name (as-is, since table names are typically plural)
                attr_name = child_table.lower().replace("-", "_")
                # back_populates points to the single parent reference on the child
                # Derived from FK column (author_id -> author)
                back_pop_name = fk_column.replace("_id", "") if fk_column.endswith("_id") else child_table.lower()
                back_populates = st.back_populates_template.format(attr_name=back_pop_name)
                # Type hint for one-to-many is List of related class (quoted for forward ref)
                type_hint = f'List["{related_class}"]'
                result += st.relationship_template.format(
                    attr_name=attr_name,
                    type_hint=type_hint,
                    related_class=related_class,
                    back_populates=back_populates,
                )
        return result

    def _add_table_args(
        self, model: str, table: Dict, schema_global: bool = True
    ) -> str:
        """Add __table_args__ to model."""
        statements = []

        if table.indexes:
            for index in table.indexes:
                if not index["unique"]:
                    self.im_index = True
                    statements.append(
                        st.index_template.format(
                            columns=", ".join(f"'{c}'" for c in index["columns"]),
                            name=f"'{index['index_name']}'",
                        )
                    )
                else:
                    self.constraint = True
                    statements.append(
                        st.unique_index_template.format(
                            columns=", ".join(f"'{c}'" for c in index["columns"]),
                            name=f"'{index['index_name']}'",
                        )
                    )

        if not schema_global and table.table_schema:
            statements.append(st.schema.format(schema_name=table.table_schema))

        if statements:
            model += st.table_args.format(statements=",".join(statements))

        return model

    def _build_datetime_import(self) -> str:
        """Build datetime import statement."""
        if not (self.datetime_import or self.date_import or self.time_import):
            return ""
        imports = []
        if self.datetime_import:
            imports.append("datetime")
        if self.date_import:
            imports.append("date")
        if self.time_import:
            imports.append("time")
        return f"from datetime import {', '.join(imports)}\n"

    def create_header(
        self, tables: List[Dict], schema: bool = False, *args, **kwargs
    ) -> str:
        """Generate file header with imports."""
        parts = []

        parts.append(self._build_datetime_import())

        if self.uuid_import:
            parts.append("from uuid import UUID\n")

        if self.typing_imports:
            parts.append(st.typing_import.format(types=", ".join(sorted(self.typing_imports))) + "\n")

        if "func" in self.state:
            parts.append(st.sql_alchemy_func_import + "\n")

        if self.postgresql_dialect_cols:
            parts.append(st.postgresql_dialect_import.format(
                types=", ".join(sorted(self.postgresql_dialect_cols))) + "\n")

        if self.fk_import:
            parts.append("from sqlalchemy import ForeignKey\n")

        if self.constraint:
            parts.append(st.unique_cons_import + "\n")

        if self.im_index:
            parts.append(st.index_import + "\n")

        if self.relationship_import:
            parts.append(st.relationship_import + "\n")

        return "".join(parts)
