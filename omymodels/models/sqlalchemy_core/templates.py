# imports
postgresql_dialect_import = "from sqlalchemy.dialects.postgresql import {types}"
sql_alchemy_func_import = "from sqlalchemy.sql import func"
index_import = "from sqlalchemy import Index"

unique_cons_import = "from sqlalchemy.schema import UniqueConstraint"

# model defenition
table_template = """\n
{table_var} = Table("{table_name}", metadata,
{columns}{constraints}{schema})
"""

# columns defenition
column_template = """        Column({column_type}{properties})"""
required = ", nullable=False"
default = ", server_default={default}"
pk_template = ", primary_key=True"
unique = ", unique=True"
autoincrement = ", autoincrement=True"
index = ", index=True"


fk_constraint_template = """
    {fk_name} = sa.ForeignKeyConstraint(
        [{fk_columns}], [{fk_references_columns}])
"""
fk_in_column = ", sa.ForeignKey('{ref_table}.{ref_column}')"
unique_index_template = """        UniqueConstraint({columns}, name={name}),\n"""

index_template = """\nIndex({name}, {columns})"""

schema = '        schema="{schema_name}"'

on_delete = ', ondelete="{mode}"'
on_update = ', onupdate="{mode}"'
