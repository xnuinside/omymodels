from typing import Dict, List, Optional

from table_meta.model import Column

import omymodels.models.sqlmodel.templates as st
from omymodels import logic, types
from omymodels.helpers import create_class_name, datetime_now_check
from omymodels.models.sqlmodel.types import types_mapping
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

    def add_custom_type_orm(
        self, custom_types: Dict, column_data_type: str, column_type: str
    ) -> dict:
        column_type_data = None
        if "." in column_data_type:
            column_data_type = column_data_type.split(".")[1]
        column_type = custom_types.get(column_data_type, column_type)

        if isinstance(column_type, tuple):
            column_data_type = column_type[1]
            column_type = column_type[0]
        if column_type is not None:
            column_type_data = {
                "pydantic": column_data_type,
                "sa": f"{column_type}({column_data_type})",
            }
        return column_type_data

    def prepare_column_type(self, column_data: Column) -> str:
        column_type = None
        column_data = types.prepare_column_data(column_data)

        if self.custom_types:
            column_type = self.add_custom_type_orm(
                self.custom_types, column_data.type, column_type
            )

        if not column_type:
            column_type = types.prepare_type(column_data, self.types_mapping)
        if column_type["sa"] in types.postgresql_dialect:
            self.postgresql_dialect_cols.add(column_type["sa"])

        if "[" in column_data.type and column_data.type not in types.json_types:
            # @TODO: How do we handle arrays for SQLModel?
            self.postgresql_dialect_cols.add("ARRAY")
            column_type = f"ARRAY({column_type})"
        return column_type

    def add_table_args(
        self, model: str, table: Dict, schema_global: bool = True
    ) -> str:
        statements = []
        t = self.templates
        if table.indexes:
            for index in table.indexes:
                if not index["unique"]:
                    self.im_index = True
                    statements.append(
                        t.index_template.format(
                            columns="', '".join(index["columns"]),
                            name=f"'{index['index_name']}'",
                        )
                    )
                else:
                    self.constraint = True
                    statements.append(
                        t.unique_index_template.format(
                            columns=",".join(index["columns"]),
                            name=f"'{index['index_name']}'",
                        )
                    )
        if not schema_global and table.table_schema:
            statements.append(t.schema.format(schema_name=table.table_schema))
        if statements:
            model += t.table_args.format(statements=",".join(statements))
        return model

    def generate_model(
        self,
        table: Dict,
        singular: bool = True,
        exceptions: Optional[List] = None,
        schema_global: Optional[bool] = True,
        *args,
        **kwargs,
    ) -> str:
        """method to prepare one Model defention - name & tablename  & columns"""

        model = st.model_template.format(
            model_name=create_class_name(table.name, singular, exceptions),
            table_name=table.name,
        )
        for column in table.columns:
            column_type = self.prepare_column_type(column)
            pydantic_type_str = column_type["pydantic"]
            if column.nullable or column.name in table.primary_key:
                pydantic_type_str = f"Optional[{pydantic_type_str}]"
            col_str = st.column_template.format(
                column_name=column.name.replace(" ", "_"), column_type=pydantic_type_str
            )
            attrs_col_str = logic.setup_column_attributes(
                column, table.primary_key, "", table, schema_global, st, self
            )
            if column_type["sa"]:
                sa_type = types.add_size_to_orm_column(column_type["sa"], column)
                attrs_col_str += st.sa_type.format(satype=sa_type)
            if attrs_col_str:
                attrs_col_str = attrs_col_str.replace(",", "", 1).strip()
                col_str += st.field_template.format(attr_data=attrs_col_str)
            col_str += "\n"
            model += col_str
        if table.indexes or table.alter or table.checks or not schema_global:
            model = self.add_table_args(model, table, schema_global)
        return model

    def create_header(
        self,
        tables: List[Dict],
        models_str: str,
        schema: bool = False,
    ) -> str:
        """header of the file - imports & sqlalchemy init"""
        header = ""
        if "sa." in models_str:
            header += st.sqlalchemy_import  # Do we always need this import?
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
        return header
