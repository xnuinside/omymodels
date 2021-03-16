# imports
postgresql_dialect_import = "from sqlalchemy.dialects.postgresql import {types}"
sql_alchemy_func_import = "from sqlalchemy.sql import func"
uniquer_constraint_import = "from sqlalchemy import UniqueConstraint"

gino_import = "from gino import Gino"

gino_init = "db = Gino()"
gino_init_schema = 'db = Gino(schema="{schema}")'

# model defenition
model_template = """

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
fk_template = """
    {fk_name} = db.ForeignKeyConstraint(
        [{fk_columns}], [{fk_references_columns}])
"""
