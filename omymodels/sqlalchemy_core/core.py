from typing import Optional, List, Dict
import omymodels.sqlalchemy_core.templates as st
from omymodels.sqlalchemy_core.types import (
    types_mapping,
    postgresql_dialect,
    datetime_types,
)
from omymodels.utils import create_class_name, type_not_found, enum_number_name_list
from omymodels.meta_model import Column


class ModelGenerator:
    def __init__(self):
        self.state = set()
        self.postgresql_dialect_cols = set()
        self.constraint = False
        self.im_index = False
        self.enum_imports = set()
        self.custom_types = {}

    def add_custom_type(self, column_data_type: str, column_type: str) -> str:
        column_type = self.custom_types.get(column_data_type, column_type)
        if isinstance(column_type, tuple):
            column_data_type = column_type[1]
            column_type = column_type[0]
        if column_type != type_not_found:
            column_type = f"{column_type}({column_data_type})"
            self.no_need_par = True
        return column_type

    def prepare_column_type(self, column_data: Dict) -> str:
        """ extract and map column type """
        self.no_need_par = False
        column_type = type_not_found
        if "." in column_data.type:
            column_data_type = column_data.type.split(".")[1]
        else:
            column_data_type = column_data.type.lower().split("[")[0]
        if self.custom_types:
            column_type = self.add_custom_type(column_data_type, column_type)
        if column_type == type_not_found:
            column_type = types_mapping.get(column_data_type, column_type)
        if column_type in postgresql_dialect:
            self.postgresql_dialect_cols.add(column_type)
        if column_type == "UUID":
            self.no_need_par = True
        if column_data.size:
            column_type = self.add_size_to_column_type(column_data.size)
        elif self.no_need_par is False:
            column_type += "()"

        if "[" in column_data.type:
            self.postgresql_dialect_cols.add("ARRAY")
            column_type = f"ARRAY({column_type})"
        return column_type

    @staticmethod
    def add_size_to_column_type(size):
        if isinstance(size, int):
            return f"({size})"
        elif isinstance(size, tuple):
            return f"({','.join([str(x) for x in size])})"

    def column_default(self, column_data: Dict) -> str:
        """ extract & format column default values """
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
        default_property = st.default.format(default=column_data.default)
        return default_property

    def get_column_attributes(
        self, column_data: Dict, table_pk: List[str], table_data: Dict
    ) -> List[str]:
        properties = []
        if (
            column_data.type.lower() == "serial"
            or column_data.type.lower() == "bigserial"
        ):
            properties.append(st.autoincrement)
        if column_data.references:
            properties.append(
                self.column_reference(column_data.name, column_data.references)
            )
        if not column_data.nullable and column_data.name not in table_pk:
            properties.append(st.required)
        if column_data.default is not None:
            properties.append(self.column_default(column_data))
        if column_data.name in table_pk:
            properties.append(st.pk_template)
        if column_data.unique:
            properties.append(st.unique)
        if "columns" in table_data.alter:
            for alter_column in table_data.alter["columns"]:
                if (
                    alter_column["name"] == column_data.name
                    and not alter_column["constraint_name"]
                    and alter_column["references"]
                    and not column_data.references
                ):
                    properties.append(
                        self.column_reference(
                            alter_column["name"], alter_column["references"]
                        )
                    )
        return properties

    @staticmethod
    def column_reference(column_name: str, reference: Dict[str, str]) -> str:
        """ ForeignKey property creator """
        ref_property = st.fk_in_column.format(
            ref_table=reference["table"], ref_column=reference["column"] or column_name
        )
        if reference["on_delete"]:
            ref_property += st.on_delete.format(mode=reference["on_delete"].upper())
        if reference["on_update"]:
            ref_property += st.on_update.format(mode=reference["on_update"].upper())
        return ref_property

    def generate_column(
        self, column_data: Column, table_pk: List[str], table_data: Dict
    ) -> str:
        """ method to generate full column defention """
        column_type = self.prepare_column_type(column_data)
        properties = "".join(
            self.get_column_attributes(column_data, table_pk, table_data)
        )

        column = st.column_template.format(
            column_name=column_data.name,
            column_type=column_type,
            properties=properties,
        )
        return column + ",\n"

    def get_indexes_and_unique(
        self, model: str, table: Dict, table_var_name: str
    ) -> str:
        indexes = []
        unique_constr = []
        if table.indexes:
            for index in table.indexes:
                if not index["unique"]:
                    self.im_index = True
                    indexes.append(
                        st.index_template.format(
                            columns=",".join(
                                [
                                    f"{table_var_name}.c.{name}"
                                    for name in index["columns"]
                                ]
                            ),
                            name=f"'{index['index_name']}'",
                        )
                    )
                else:
                    self.constraint = True
                    unique_constr.append(
                        st.unique_index_template.format(
                            columns=",".join(
                                [f"'{name}'" for name in index["columns"]]
                            ),
                            name=f"'{index['index_name']}'",
                        )
                    )
        return indexes, unique_constr

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

    def generate_model(self, data: Dict, *args, **kwargs) -> str:
        """ method to prepare one Model defention - name & tablename  & columns """
        model = ""
        # mean this is a table
        table = data
        columns = ""

        for column in table.columns:
            columns += self.generate_column(column, table.primary_key, table)

        table_var_name = table.name.replace("-", "_")

        indexes = []
        constraints = None

        if table.indexes or table.alter or table.checks:
            indexes, constraints = self.get_indexes_and_unique(
                model, table, table_var_name
            )

        model = st.table_template.format(
            table_var=table_var_name,
            table_name=table.name,
            columns=columns,
            schema=""
            if not table.table_schema
            else st.schema.format(schema_name=table.table_schema),
            constraints=", ".join(constraints) if constraints else "",
        )
        for index in indexes:
            model += index
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
