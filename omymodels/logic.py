from typing import Dict, List
import omymodels.types as t


def generate_column(
    column_data: Dict, table_pk: List[str], table_data: Dict, templates, obj
) -> str:
    """ method to generate full column defention for sqlalchemy & gino ORM models """
    column_type = t.prepare_column_type_orm(obj, column_data)
    column = templates.column_template.format(
        column_name=column_data.name, column_type=column_type
    )
    column = setup_column_attributes(
        column_data, table_pk, column, table_data, templates, obj
    )
    column += ")\n"
    return column


def setup_column_attributes(
    column_data: Dict,
    table_pk: List[str],
    column: str,
    table_data: Dict,
    templates,
    obj,
) -> str:

    if column_data.type.lower() == "serial" or column_data.type.lower() == "bigserial":
        column += templates.autoincrement
    if column_data.references:
        column = add_reference_to_the_column(
            column_data.name, column, column_data.references, templates
        )
    if not column_data.nullable and column_data.name not in table_pk:
        column += templates.required
    if column_data.default is not None:
        column = obj.prepare_column_default(column_data, column)
    if column_data.name in table_pk:
        column += templates.pk_template
    if column_data.unique:
        column += templates.unique

    if "columns" in table_data.alter:
        for alter_column in table_data.alter["columns"]:
            if (
                alter_column["name"] == column_data.name
                and not alter_column["constraint_name"]
                and alter_column["references"]
            ):

                column = add_reference_to_the_column(
                    alter_column["name"], column, alter_column["references"], templates
                )
    return column


def add_reference_to_the_column(
    column_name: str, column: str, reference: Dict[str, str], templates
) -> str:
    column += templates.fk_in_column.format(
        ref_table=reference["table"], ref_column=reference["column"] or column_name
    )
    if reference["on_delete"]:
        column += templates.on_delete.format(mode=reference["on_delete"].upper())
    if reference["on_update"]:
        column += templates.on_update.format(mode=reference["on_update"].upper())
    return column


def add_table_args(obj, model: str, table: Dict, schema_global: bool = True) -> str:
    statements = []
    t = obj.templates
    if table.indexes:
        for index in table.indexes:

            if not index["unique"]:
                obj.im_index = True
                statements.append(
                    t.index_template.format(
                        columns=",".join(index["columns"]),
                        name=f"'{index['index_name']}'",
                    )
                )
            else:
                obj.constraint = True
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
