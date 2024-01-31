from omymodels import create_models


def test_unique_and_index():
    expected = """import sqlalchemy as sa
from sqlalchemy import Table, Column, MetaData
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy import Index


metadata = MetaData()


table = Table("table", metadata,
        Column(UUID, primary_key=True),
        Column(sa.Integer()),
        UniqueConstraint('one_more_id', name='table_pk'),
        schema="prefix--schema-name")

Index('table_ix2', table.c._id)"""
    ddl = """
    CREATE TABLE "prefix--schema-name"."table" (
    _id uuid PRIMARY KEY,
    one_more_id int
    );
        create unique index table_pk on "prefix--schema-name"."table" (one_more_id) ;
        create index table_ix2 on "prefix--schema-name"."table" (_id) ;
    """

    result = create_models(ddl, models_type="sqlalchemy_core")["code"]
    assert expected == result


def test_foreign_keys_with_schema():
    expected = """import sqlalchemy as sa
from sqlalchemy import Table, Column, MetaData


metadata = MetaData()


materials = Table("materials", metadata,
        Column(sa.Integer(), primary_key=True),
        Column(sa.String(), nullable=False),
        Column(sa.String()),
        Column(sa.String()),
        Column(sa.TIMESTAMP()),
        Column(sa.TIMESTAMP()),
)


material_attachments = Table("material_attachments", metadata,
        Column(sa.Integer(), sa.ForeignKey('materials.id')),
        Column(sa.Integer(), sa.ForeignKey('attachments.id')),
        schema="schema_name")


attachments = Table("attachments", metadata,
        Column(sa.Integer(), primary_key=True),
        Column(sa.String()),
        Column(sa.String()),
        Column(sa.TIMESTAMP()),
        Column(sa.TIMESTAMP()),
)
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

    CREATE TABLE "schema_name"."material_attachments" (
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


    ALTER TABLE "schema_name"."material_attachments" ADD FOREIGN KEY ("material_id") REFERENCES "materials" ("id");

    ALTER TABLE "schema_name"."material_attachments" ADD FOREIGN KEY ("attachment_id") REFERENCES "attachments" ("id");
"""

    result = create_models(ddl, models_type="sqlalchemy_core")["code"]
    assert result == expected


def test_keyword_args():
    expected = """import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Merchants(Base):

    __tablename__ = 'merchants'

    id = sa.Column(sa.Integer(), primary_key=True)
    merchant_name = sa.Column(sa.String())


class Products(Base):

    __tablename__ = 'products'

    id = sa.Column(sa.Integer(), primary_key=True)
    merchant_id = sa.Column(sa.Integer(), sa.ForeignKey('merchants.id'), nullable=False)
"""

    ddl = """
    CREATE TABLE "merchants" (
    "id" int PRIMARY KEY,
    "merchant_name" varchar
    );

    CREATE TABLE "products" (
    "ID" int PRIMARY KEY,
    "merchant_id" int NOT NULL
    );

    ALTER TABLE "products" ADD FOREIGN KEY ("merchant_id") REFERENCES "merchants" ("id");
    """
    result = create_models(ddl, models_type="sqlalchemy")["code"]
    assert result == expected


def test_real():
    expected = """import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Measurements(Base):

    __tablename__ = 'measurements'

    id = sa.Column(sa.String(32), primary_key=True)
    date = sa.Column(sa.TIMESTAMP())
    value = sa.Column(sa.REAL())
"""

    ddl = """
    CREATE TABLE "measurements" (
        "id" char(32) PRIMARY KEY NOT NULL,
        "date" timestamp,
        "value" real,
    );"""

    result = create_models(ddl, models_type="sqlalchemy")["code"]
    assert result == expected
