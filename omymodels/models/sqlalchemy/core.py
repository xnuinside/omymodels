from typing import Dict, List, Optional

import omymodels.models.sqlalchemy.templates as st
from omymodels import logic
from omymodels.helpers import create_class_name, datetime_now_check
from omymodels.models.sqlalchemy.types import types_mapping
from omymodels.types import datetime_types


class GeneratorBase:
    def __init__(self):
        self.custom_types = {}


class ModelGenerator(GeneratorBase):
    def __init__(self):
        self.state = set()
        self.postgresql_dialect_cols = set()
        self.constraint = False
        self.im_index = False
        self.relationship_import = False
        self.types_mapping = types_mapping
        self.templates = st
        self.prefix = "sa."
        super().__init__()

    def prepare_column_default(self, column_data: Dict, column: str) -> str:
        if isinstance(column_data.default, str):
            if column_data.type.upper() in datetime_types:
                if datetime_now_check(column_data.default.lower()):
                    # todo: need to add other popular PostgreSQL & MySQL functions
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
        """method to prepare one Model defention - name & tablename  & columns"""
        model = ""
        model_name = create_class_name(table.name, singular, exceptions)

        model = st.model_template.format(
            model_name=model_name,
            table_name=table.name,
        )
        for column in table.columns:
            model += logic.generate_column(
                column, table.primary_key, table, schema_global, st, self
            )
        if table.indexes or table.alter or table.checks or not schema_global:
            model = logic.add_table_args(self, model, table, schema_global)

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

        for rel in relationships:
            if rel["type"] == "many_to_one":
                # Child side: reference to parent
                # e.g., posts.user = relationship("Users", back_populates="posts")
                ref_table = rel["ref_table"]
                fk_column = rel["fk_column"]
                child_table_name = rel["child_table_name"]
                related_class = create_class_name(ref_table, singular, exceptions)
                # Attribute name derived from FK column (user_id -> user)
                attr_name = fk_column.replace("_id", "") if fk_column.endswith("_id") else ref_table.lower()
                # back_populates points to the collection on the parent (uses child table name)
                back_pop_name = child_table_name.lower().replace("-", "_")
                back_populates = st.back_populates_template.format(attr_name=back_pop_name)
                result += st.relationship_template.format(
                    attr_name=attr_name,
                    related_class=related_class,
                    back_populates=back_populates,
                )
            elif rel["type"] == "one_to_many":
                # Parent side: collection of children
                # e.g., users.posts = relationship("Posts", back_populates="user")
                child_table = rel["child_table"]
                fk_column = rel["fk_column"]
                related_class = create_class_name(child_table, singular, exceptions)
                # Attribute name is the child table name (as-is, since table names are typically plural)
                attr_name = child_table.lower().replace("-", "_")
                # back_populates points to the single parent reference on the child
                # Derived from FK column (user_id -> user)
                back_pop_name = fk_column.replace("_id", "") if fk_column.endswith("_id") else child_table.lower()
                back_populates = st.back_populates_template.format(attr_name=back_pop_name)
                result += st.relationship_template.format(
                    attr_name=attr_name,
                    related_class=related_class,
                    back_populates=back_populates,
                )
        return result

    def create_header(
        self, tables: List[Dict], schema: bool = False, *args, **kwargs
    ) -> str:
        """header of the file - imports & sqlalchemy init"""
        header = ""
        if "func" in self.state:
            header += st.sql_alchemy_func_import + "\n"
        if self.postgresql_dialect_cols:
            header += (
                st.postgresql_dialect_import.format(
                    types=",".join(self.postgresql_dialect_cols)
                )
                + "\n"
            )
        if self.constraint:
            header += st.unique_cons_import + "\n"
        if self.im_index:
            header += st.index_import + "\n"
        if self.relationship_import:
            header += st.relationship_import + "\n"
        return header
