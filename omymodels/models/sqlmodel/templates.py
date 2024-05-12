# imports
postgresql_dialect_import = """from sqlalchemy.dialects.postgresql import {types}
from pydantic import Json, UUID4"""
sql_alchemy_func_import = "from sqlalchemy.sql import func"
index_import = "from sqlalchemy import Index"

sqlalchemy_import = """import sqlalchemy as sa
"""

unique_cons_import = "from sqlalchemy.schema import UniqueConstraint"
enum_import = "from enum import {enums}"

# model defenition
model_template = """\n
class {model_name}(SQLModel, table=True):\n
    __tablename__ = \'{table_name}\'\n
"""

# columns defenition
column_template = """    {column_name}: {column_type}"""
field_template = """ = Field({attr_data})"""
required = ""
default = ", sa_column_kwargs={{'server_default': {default}}}"
pk_template = ", default=None, primary_key=True"
unique = ", unique=True"
autoincrement = ""
index = ", index=True"
sa_type = ", sa_type={satype}"

# tables properties

table_args = """
    __table_args__ = (
                {statements},
            )

"""
fk_constraint_template = """
    {fk_name} = sa.ForeignKeyConstraint(
        [{fk_columns}], [{fk_references_columns}])
"""
fk_in_column = ", foreign_key='{ref_schema}.{ref_table}.{ref_column}'"
fk_in_column_without_schema = ", foreign_key='{ref_table}.{ref_column}'"

unique_index_template = """
    UniqueConstraint({columns}, name={name})"""

index_template = """
    Index({name}, '{columns}')"""

schema = """
    dict(schema="{schema_name}")"""

on_delete = ', ondelete="{mode}"'
on_update = ', onupdate="{mode}"'
