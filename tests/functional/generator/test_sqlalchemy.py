from omymodels import create_models


def test_with_enums():
    expected = """import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON


Base = declarative_base()


class MaterialType(str, Enum):

    article = 'article'
    video = 'video'
    

class Material(Base):

    __tablename__ = 'material'

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    title = sa.Column(sa.String(), nullable=False)
    description = sa.Column(sa.Text())
    link = sa.Column(sa.String(), nullable=False)
    type = sa.Column(sa.Enum(MaterialType))
    additional_properties = sa.Column(JSON(), server_default='{"key": "value"}')
    created_at = sa.Column(sa.TIMESTAMP(), server_default=func.now())
    updated_at = sa.Column(sa.TIMESTAMP())
"""
    ddl = """
CREATE TYPE "material_type" AS ENUM (
  'video',
  'article'
);

CREATE TABLE "material" (
  "id" SERIAL PRIMARY KEY,
  "title" varchar NOT NULL,
  "description" text,
  "link" varchar NOT NULL,
  "type" material_type,
  "additional_properties" json DEFAULT '{"key": "value"}',
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp
);
"""
    result = create_models(ddl, models_type="sqlalchemy")
    assert expected == result["code"]


def test_foreign_keys():
    expected = """import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Materials(Base):

    __tablename__ = 'materials'

    id = sa.Column(sa.Integer(), primary_key=True)
    title = sa.Column(sa.String(), nullable=False)
    description = sa.Column(sa.String())
    link = sa.Column(sa.String())
    created_at = sa.Column(sa.TIMESTAMP())
    updated_at = sa.Column(sa.TIMESTAMP())


class MaterialAttachments(Base):

    __tablename__ = 'material_attachments'

    material_id = sa.Column(sa.Integer(), sa.ForeignKey('materials.id'))
    attachment_id = sa.Column(sa.Integer(), sa.ForeignKey('attachments.id'))


class Attachments(Base):

    __tablename__ = 'attachments'

    id = sa.Column(sa.Integer(), primary_key=True)
    title = sa.Column(sa.String())
    description = sa.Column(sa.String())
    created_at = sa.Column(sa.TIMESTAMP())
    updated_at = sa.Column(sa.TIMESTAMP())
"""
    ddl = """

  CREATE TABLE "materials" (
  "id" int PRIMARY KEY,
  "title" varchar NOT NULL,
  "description" varchar,
  "link" varchar,
  "created_at" timestamp,
  "updated_at" timestamp
  );

  CREATE TABLE "material_attachments" (
  "material_id" int,
  "attachment_id" int
  );

  CREATE TABLE "attachments" (
  "id" int PRIMARY KEY,
  "title" varchar,
  "description" varchar,
  "created_at" timestamp,
  "updated_at" timestamp
  );


  ALTER TABLE "material_attachments" ADD FOREIGN KEY ("material_id") REFERENCES "materials" ("id");

  ALTER TABLE "material_attachments" ADD FOREIGN KEY ("attachment_id") REFERENCES "attachments" ("id");

  """
    result = create_models(ddl, models_type="sqlalchemy")["code"]
    assert result == expected


def test_foreign_keys_defined_inline():
    """
    This should be the same output as test_foreign_keys, but with a slightly
    different, yet valid input DDL.
    """
    expected = """import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Materials(Base):

    __tablename__ = 'materials'

    id = sa.Column(sa.Integer(), primary_key=True)
    title = sa.Column(sa.String(), nullable=False)
    description = sa.Column(sa.String())
    link = sa.Column(sa.String())
    created_at = sa.Column(sa.TIMESTAMP())
    updated_at = sa.Column(sa.TIMESTAMP())


class MaterialAttachments(Base):

    __tablename__ = 'material_attachments'

    material_id = sa.Column(sa.Integer(), sa.ForeignKey('materials.id'))
    attachment_id = sa.Column(sa.Integer(), sa.ForeignKey('attachments.id'))


class Attachments(Base):

    __tablename__ = 'attachments'

    id = sa.Column(sa.Integer(), primary_key=True)
    title = sa.Column(sa.String())
    description = sa.Column(sa.String())
    created_at = sa.Column(sa.TIMESTAMP())
    updated_at = sa.Column(sa.TIMESTAMP())
"""
    ddl = """

  CREATE TABLE "materials" (
  "id" int PRIMARY KEY,
  "title" varchar NOT NULL,
  "description" varchar,
  "link" varchar,
  "created_at" timestamp,
  "updated_at" timestamp
  );

  CREATE TABLE "material_attachments" (
  "material_id" int,
  "attachment_id" int,
  CONSTRAINT "material_id_ibfk" FOREIGN KEY ("material_id") REFERENCES "materials" ("id"),
  CONSTRAINT "attachment_id_ibfk" FOREIGN KEY ("attachment_id") REFERENCES "attachments" ("id")
  );

  CREATE TABLE "attachments" (
  "id" int PRIMARY KEY,
  "title" varchar,
  "description" varchar,
  "created_at" timestamp,
  "updated_at" timestamp
  );
  """
    result = create_models(ddl, models_type="sqlalchemy")["code"]
    assert result == expected


def test_multi_col_pk_and_fk():
    """
    This should test that we can properly setup tables with compound PRIMARY and
    FOREIGN keys.
    """
    expected = """import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


class Complexpk(Base):

    __tablename__ = 'complexpk'

    complex_id = sa.Column(int unsigned(), primary_key=True)
    date_part = sa.Column(sa.DateTime(), server_default=func.now(), primary_key=True)
    title = sa.Column(sa.String(), nullable=False)
    description = sa.Column(sa.String())


class LinkedTo(Base):

    __tablename__ = 'linked_to'

    id = sa.Column(sa.Integer(), primary_key=True)
    complexpk_complex_id = sa.Column(sa.Integer(), sa.ForeignKey('complexpk.complex_id'))
    complexpk_date_part = sa.Column(sa.Integer(), sa.ForeignKey('complexpk.date_part'))
    comment = sa.Column(sa.String())
"""

    ddl = """

  CREATE TABLE "complexpk" (
  "complex_id" int unsigned NOT NULL,
  "date_part" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "title" varchar NOT NULL,
  "description" varchar,
  PRIMARY KEY ("complex_id","date_part")
  );

  CREATE TABLE "linked_to" (
  "id" int PRIMARY KEY,
  "complexpk_complex_id" int,
  "complexpk_date_part" int,
  "comment" varchar,
  CONSTRAINT "id_date_part_ibfk" FOREIGN KEY ("complexpk_complex_id", "complexpk_date_part")
    REFERENCES "complexpk" ("complex_id", "date_part")
  );

  """
    result = create_models(ddl, models_type="sqlalchemy")["code"]
    assert result == expected


def test_upper_name_produces_the_same_result():
    expected = """import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON


Base = declarative_base()


class MaterialType(str, Enum):

    article = 'article'
    video = 'video'
    

class Material(Base):

    __tablename__ = 'material'

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    title = sa.Column(sa.String(), nullable=False)
    description = sa.Column(sa.Text())
    link = sa.Column(sa.String(), nullable=False)
    type = sa.Column(sa.Enum(MaterialType))
    additional_properties = sa.Column(JSON(), server_default='{"key": "value"}')
    created_at = sa.Column(sa.TIMESTAMP(), server_default=func.now())
    updated_at = sa.Column(sa.TIMESTAMP())
"""
    ddl = """
CREATE TYPE "material_type" AS ENUM (
  'video',
  'article'
);

CREATE TABLE "material" (
  "id" SERIAL PRIMARY KEY,
  "title" varchar NOT NULL,
  "description" text,
  "link" varchar NOT NULL,
  "type" material_type,
  "additional_properties" json DEFAULT '{"key": "value"}',
  "created_at" timestamp DEFAULT (NOW()),
  "updated_at" timestamp
);
"""
    result = create_models(ddl, models_type="sqlalchemy")
    assert expected == result["code"]


def test_foreign_keys_in_different_schema():
    expected = """import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Table1(Base):

    __tablename__ = 'table1'

    id = sa.Column(sa.Integer(), primary_key=True)
    reference_to_table_in_another_schema = sa.Column(sa.Integer(), sa.ForeignKey('schema2.table2.id'), nullable=False)

    __table_args__ = (
                
    dict(schema="schema1")
            )



class Table2(Base):

    __tablename__ = 'table2'

    id = sa.Column(sa.Integer(), primary_key=True)

    __table_args__ = (
                
    dict(schema="schema2")
            )

"""
    ddl = """
CREATE SCHEMA "schema1";

CREATE SCHEMA "schema2";

CREATE TABLE "schema1"."table1" (
  "id" int PRIMARY KEY,
  "reference_to_table_in_another_schema" int NOT NULL
);

CREATE TABLE "schema2"."table2" (
  "id" int PRIMARY KEY
);

ALTER TABLE "schema1"."table1" ADD FOREIGN KEY
("reference_to_table_in_another_schema") REFERENCES "schema2"."table2" ("id");
"""
    result = create_models(ddl, schema_global=False, models_type="sqlalchemy")["code"]
    assert result == expected
