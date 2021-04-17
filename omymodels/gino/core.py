from typing import Optional, List, Dict
import omymodels.gino.templates as gt
from omymodels.gino.types import types_mapping, postgresql_dialect, datetime_types
from omymodels.utils import create_class_name, type_not_found, enum_number_name_list


class ModelGenerator:
    def __init__(self):
        self.state = set()
        self.postgresql_dialect_cols = set()
        self.constraint = False
        self.im_index = False
        self.enum_imports = set()
        self.custom_types = {}

    def prepare_column_type(self, column_data: Dict) -> str:
        no_need_par = False
        column_type = type_not_found
        if "." in column_data["type"]:
            column_data_type = column_data["type"].split(".")[1]
        else:
            column_data_type = column_data["type"].lower().split("[")[0]
        if self.custom_types:
            column_type = self.custom_types.get(column_data_type, column_type)
            if column_type != type_not_found:
                column_type = f"{column_type}({column_data_type})"
                no_need_par = True
        if column_type == type_not_found:
            column_type = types_mapping.get(column_data_type, column_type)
        if column_type in postgresql_dialect:
            self.postgresql_dialect_cols.add(column_type)
        if column_type == 'UUID':
            no_need_par = True
        if column_data["size"]:
            if isinstance(column_data["size"], int):
                column_type += f"({column_data['size']})"
            elif isinstance(column_data["size"], tuple):
                column_type += f"({','.join([str(x) for x in column_data['size']])})"
        elif no_need_par is False:
            column_type += f"()"

        if "[" in column_data["type"]:
            self.postgresql_dialect_cols.add("ARRAY")
            column_type = f"ARRAY({column_type})"
        column = gt.column_template.format(
            column_name=column_data["name"], column_type=column_type
        )
        return column

    def prepare_column_default(self, column_data: Dict, column: str) -> str:
        if isinstance(column_data["default"], str):
            if column_data["type"].upper() in datetime_types:
                if "now" in column_data["default"]:
                    # todo: need to add other popular PostgreSQL & MySQL functions
                    column_data["default"] = "func.now()"
                    self.state.add("func")
                elif "'" not in column_data["default"]:
                    column_data["default"] = f"'{column_data['default']}'"
            else:
                if "'" not in column_data["default"]:
                    column_data["default"] = f"'{column_data['default']}'"
        else:
            column_data["default"] = f"'{str(column_data['default'])}'"
        column += gt.default.format(default=column_data["default"])
        return column

    def setup_column_attributes(
        self, column_data: Dict, table_pk: List[str], column: str, table_data: Dict
    ) -> str:

        if (
            column_data["type"].lower() == "serial"
            or column_data["type"].lower() == "bigserial"
        ):
            column += gt.autoincrement
        if column_data["references"]:
            column = self.add_reference_to_the_column(column_data["name"], column, column_data["references"])
        if not column_data["nullable"] and not column_data["name"] in table_pk:
            column += gt.required
        if column_data["default"] is not None:
            column = self.prepare_column_default(column_data, column)
        if column_data["name"] in table_pk:
            column += gt.pk_template
        if column_data["unique"]:
            column += gt.unique
        
        if 'columns' in table_data["alter"]:
            for alter_column in table_data["alter"]['columns']:
                if alter_column['name'] == column_data[
                    "name"] and not alter_column[
                        'constraint_name'] and alter_column['references']:
                    
                    column = self.add_reference_to_the_column(alter_column['name'], column, alter_column['references'])
        return column
    
    @staticmethod
    def add_reference_to_the_column(column_name: str, column: str, reference: Dict[str, str]) -> str:
        column += gt.fk_in_column.format(ref_table=reference['table'], 
                                        ref_column=reference['column'] or column_name)
        if reference['on_delete']:
            column += gt.on_delete.format(mode=reference['on_delete'].upper())
        if reference['on_update']:
            column += gt.on_update.format(mode=reference['on_update'].upper())
        return column
                    
    def generate_column(self, column_data: Dict, table_pk: List[str], table_data: Dict) -> str:
        """ method to generate full column defention """
        column = self.setup_column_attributes(
            column_data, table_pk, self.prepare_column_type(column_data), table_data
        )
        column += ")\n"
        return column

    def add_table_args(self, model: str, table: Dict, schema_global: bool = True) -> str:
        statements = []
        if table.get("index"):
            for index in table["index"]:

                if not index["unique"]:
                    self.im_index = True
                    statements.append(
                        gt.index_template.format(
                            columns=",".join(index["columns"]),
                            name=f"'{index['index_name']}'",
                        )
                    )
                else:
                    self.constraint = True
                    statements.append(
                        gt.unique_index_template.format(
                            columns=",".join(index["columns"]),
                            name=f"'{index['index_name']}'",
                        )
                    )
        if not schema_global and table['schema']:
            statements.append(gt.schema.format(schema_name=table['schema']))
        if statements:
            model += gt.table_args.format(statements=",".join(statements))
        return model

    def generate_type(
        self, _type: Dict, singular: bool = False, exceptions: Optional[List] = None
    ) -> str:
        """ method to prepare one Model defention - name & tablename  & columns """
        type_class = ""
            
        if _type["properties"].get("values"):
            # mean this is a Enum
            _type["properties"]["values"].sort()
            for num, value in enumerate(_type["properties"]["values"]):
                _value = value.replace("'", "")
                if not _value.isnumeric():
                    type_class += (
                        gt.enum_value.format(name=value.replace("'", ""), value=value)
                        + "\n"
                    )
                    self.enum_imports.add("Enum")
                    sub_type = "Enum"
                else:
                    type_class += (
                        gt.enum_value.format(
                            name=enum_number_name_list.get(num), value=_value
                        )
                        + "\n"
                    )
                    sub_type = "IntEnum"
                    self.enum_imports.add("IntEnum")
            type_class ="\n\n" + (
                gt.enum_class.format(
                    class_name=create_class_name(
                        _type["type_name"], singular, exceptions
                    ),
                    type = sub_type
                )
                + "\n"
            ) + "\n" + type_class
            self.custom_types[_type["type_name"]] = "db.Enum"
        return type_class

    def generate_model(
        self, 
        table: Dict, 
        singular: bool = False, 
        exceptions: Optional[List] = None,
        schema_global: Optional[bool] = True
    ) -> str:
        """ method to prepare one Model defention - name & tablename  & columns """
        model = ""
        if table.get("table_name"):
            model = gt.model_template.format(
                model_name=create_class_name(table["table_name"], singular, exceptions),
                table_name=table["table_name"],
            )
            for column in table["columns"]:
                model += self.generate_column(column, table["primary_key"], table)
        if table.get("index") or table.get("alter") or table.get("checks") or not schema_global:
            model = self.add_table_args(model, table, schema_global)
        elif table.get("sequence_name"):
            # create sequence
            ...
        return model

    def create_header(self, tables: List[Dict], schema: bool = False) -> str:
        """ header of the file - imports & gino init """
        header = ""
        if self.enum_imports:
            header += gt.enum_import.format(enums=",".join(self.enum_imports)) + "\n"
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
        header += gt.gino_import + "\n\n"
        if schema and tables[0]["schema"]:
            schema = tables[0]["schema"].replace('"', "")
            header += gt.gino_init_schema.format(schema=schema) + "\n"
        else:
            header += gt.gino_init + "\n"
        return header
