from typing import Optional, List, Dict
import omymodels.models.sqlalchemy.templates as st
from omymodels.models.sqlalchemy.types import types_mapping
from omymodels.types import datetime_types
from omymodels.helpers import create_class_name
from omymodels import logic


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
                if "now" in column_data.default.lower():
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
        *args,
        **kwargs,
    ) -> str:
        """ method to prepare one Model defention - name & tablename  & columns """
        model = ""

        model = st.model_template.format(
            model_name=create_class_name(table.name, singular, exceptions),
            table_name=table.name,
        )
        for column in table.columns:
            model += logic.generate_column(column, table.primary_key, table, st, self)
        if table.indexes or table.alter or table.checks or not schema_global:
            model = logic.add_table_args(self, model, table, schema_global)
        return model

    def create_header(self, tables: List[Dict], schema: bool = False) -> str:
        """ header of the file - imports & sqlalchemy init """
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
        return header
