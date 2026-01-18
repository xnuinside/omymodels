# imports
postgresql_dialect_import = "from sqlalchemy.dialects.postgresql import {types}"
sql_alchemy_func_import = "from sqlalchemy.sql import func"
index_import = "from sqlalchemy import Index"
typing_import = "from typing import {types}"

sqlalchemy_import = """from sqlalchemy import (
    String, Text, Integer, BigInteger, SmallInteger,
    Float, Numeric, Boolean, Date, DateTime, Time, LargeBinary, Enum
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
"""
sqlalchemy_init = """
class Base(DeclarativeBase):
    pass
"""
unique_cons_import = "from sqlalchemy.schema import UniqueConstraint"
enum_import = "from enum import {enums}"

# model definition
model_template = """\n
class {model_name}(Base):
    __tablename__ = '{table_name}'
"""

# columns definition - SQLAlchemy 2.0 style with Mapped and mapped_column
column_template = """    {column_name}: Mapped[{python_type}] = mapped_column({column_type}"""
column_template_no_type = """    {column_name}: Mapped[{python_type}] = mapped_column("""

required = ""  # Not needed with Mapped, handled via Optional
default = ", server_default={default}"
pk_template = ", primary_key=True"
unique = ", unique=True"
autoincrement = ", autoincrement=True"
index = ", index=True"
nullable = ""  # Handled by Optional in type hint

# tables properties
table_args = """
    __table_args__ = (
                {statements}
            )

"""
fk_constraint_template = """
    {fk_name} = ForeignKeyConstraint(
        [{fk_columns}], [{fk_references_columns}])
"""
fk_in_column = ", ForeignKey('{ref_schema}.{ref_table}.{ref_column}')"
fk_in_column_without_schema = ", ForeignKey('{ref_table}.{ref_column}')"

unique_index_template = """
    UniqueConstraint({columns}, name={name})"""

index_template = """
    Index({name}, {columns})"""

schema = """
    dict(schema="{schema_name}")"""

on_delete = ', ondelete="{mode}"'
on_update = ', onupdate="{mode}"'

# relationship templates
relationship_import = "from sqlalchemy.orm import relationship"
relationship_template = '    {attr_name}: Mapped[{type_hint}] = relationship("{related_class}"{back_populates})\n'
back_populates_template = ', back_populates="{attr_name}"'
