from typing import Optional, List, Dict
import omymodels.models.gino.templates as gt
from omymodels.models.gino.types import types_mapping
from omymodels.types import datetime_types
from omymodels.helpers import create_class_name
from omymodels import logic


class ModelGenerator:
    def __init__(self):
        self.state = set()
        self.postgresql_dialect_cols = set()
        self.constraint = False
        self.im_index = False
        self.custom_types = {}
        self.types_mapping = types_mapping
        self.templates = gt
        self.prefix = "db."

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
        column += gt.default.format(default=column_data.default)
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
        model = gt.model_template.format(
            model_name=create_class_name(table.name, singular, exceptions),
            table_name=table.name,
        )
        for column in table.columns:
            model += logic.generate_column(column, table.primary_key, table, gt, self)
        if table.indexes or table.alter or table.checks or not schema_global:
            model = logic.add_table_args(self, model, table, schema_global)
        # create sequence
        return model

    def create_header(self, tables: List[Dict], schema: bool = False) -> str:
        """ header of the file - imports & gino init """
        header = ""
        if "func" in self.state:
            header += gt.sql_alchemy_func_import + "\n"
        if self.postgresql_dialect_cols:
            header += (
                gt.postgresql_dialect_import.format(
                    types=",".join(self.postgresql_dialect_cols)
                )
                + "\n"
            )
        if self.constraint:
            header += gt.unique_cons_import + "\n"
        if self.im_index:
            header += gt.index_import + "\n"
        if schema and tables[0].table_schema:
            schema = tables[0].table_schema.replace('"', "")
            header += "\n" + gt.gino_init_schema.format(schema=schema)
        else:
            header += "\n" + gt.gino_init
        return header
