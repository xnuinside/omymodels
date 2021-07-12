from omymodels import create_models


def test_with_enums():
    expected = """import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON


Base = declarative_base()


class MaterialType(Enum):

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


def test_upper_name_produces_the_same_result():
    expected = """import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON


Base = declarative_base()


class MaterialType(Enum):

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