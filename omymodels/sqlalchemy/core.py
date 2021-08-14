from typing import Optional, List, Dict
import omymodels.sqlalchemy.templates as st
from omymodels.sqlalchemy.types import types_mapping
from omymodels.types import datetime_types
from omymodels.utils import create_class_name, enum_number_name_list
from omymodels import logic


class ModelGenerator:
    def __init__(self):
        self.state = set()
        self.postgresql_dialect_cols = set()
        self.constraint = False
        self.im_index = False
        self.enum_imports = set()
        self.custom_types = {}
        self.types_mapping = types_mapping
        self.templates = st

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

    def generate_type(
        self, _type: Dict, singular: bool = False, exceptions: Optional[List] = None
    ) -> str:
        """ method to prepare one Model defention - name & tablename  & columns """
        type_class = ""

        if _type.properties.get("values"):
            # mean this is a Enum
            _type.properties["values"].sort()
            for num, value in enumerate(_type.properties["values"]):
                _value = value.replace("'", "")
                if not _value.isnumeric():
                    type_class += (
                        st.enum_value.format(name=value.replace("'", ""), value=value)
                        + "\n"
                    )
                    self.enum_imports.add("Enum")
                    sub_type = "Enum"
                else:
                    type_class += (
                        st.enum_value.format(
                            name=enum_number_name_list.get(num), value=_value
                        )
                        + "\n"
                    )
                    sub_type = "IntEnum"
                    self.enum_imports.add("IntEnum")
            class_name = create_class_name(_type.name, singular, exceptions)
            type_class = (
                "\n\n"
                + (st.enum_class.format(class_name=class_name, type=sub_type) + "\n")
                + "\n"
                + type_class
            )
            self.custom_types[_type.name] = ("sa.Enum", class_name)
        return type_class

    def generate_model(
        self,
        table: Dict,
        singular: bool = False,
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
        if self.enum_imports:
            header += st.enum_import.format(enums=",".join(self.enum_imports)) + "\n"
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
