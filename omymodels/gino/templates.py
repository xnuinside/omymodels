# imports
postgresql_dialect_import = "from sqlalchemy.dialects.postgresql import {types}"
sql_alchemy_func_import = "from sqlalchemy.sql import func"
index_import = "from sqlalchemy import Index"

unique_cons_import = "from sqlalchemy.schema import UniqueConstraint"
enum_import = "from enum import {enums}"
gino_init = "db = Gino()"
gino_init_schema = 'db = Gino(schema="{schema}")'

# model defenition
model_template = """\n
class {model_name}(db.Model):\n
    __tablename__ = \'{table_name}\'\n
"""

# columns defenition
column_template = """    {column_name} = db.Column({column_type}"""
required = ", nullable=False"
default = ", server_default={default}"
pk_template = ", primary_key=True"
unique = ", unique=True"
autoincrement = ", autoincrement=True"
index = ", index=True"

# tables properties

table_args = """
    __table_args__ = ({statements})
"""
fk_constraint_template = """
    {fk_name} = db.ForeignKeyConstraint(
        [{fk_columns}], [{fk_references_columns}])
"""
fk_in_column = ", db.ForeignKey('{ref_table}.{ref_column}')"
unique_index_template = """
    UniqueConstraint({columns}, name={name})"""

index_template = """
    Index({name}, {columns})"""

schema = """
    dict(schema="{schema_name}")"""

enum_class = """class {class_name}({type}):"""
enum_value = """    {name} = {value}"""

on_delete = ', ondelete="{mode}"'
on_update = ', onupdate="{mode}"'
