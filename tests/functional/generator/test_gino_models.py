import os

from omymodels import create_models


def test_two_simple_ddl():
    ddl = """
CREATE TABLE "users" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar,
  "created_at" timestamp,
  "updated_at" timestamp,
  "country_code" int,
  "default_language" int
);

CREATE TABLE "languages" (
  "id" int PRIMARY KEY,
  "code" varchar(2) NOT NULL,
  "name" varchar NOT NULL
);
    """

    expected = """from gino import Gino

db = Gino()


class Users(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    name = db.Column(db.String())
    created_at = db.Column(db.TIMESTAMP())
    updated_at = db.Column(db.TIMESTAMP())
    country_code = db.Column(db.Integer())
    default_language = db.Column(db.Integer())


class Languages(db.Model):

    __tablename__ = 'languages'

    id = db.Column(db.Integer(), primary_key=True)
    code = db.Column(db.String(2), nullable=False)
    name = db.Column(db.String(), nullable=False)
"""
    assert expected == create_models(ddl=ddl, dump=False)["code"]
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    models = os.path.join(tests_dir, "_models.py")
    ddl_path = os.path.join(tests_dir, "test_two_tables.sql")
    create_models(ddl_path=ddl_path, dump_path=models)
    with open(models, "r") as f:
        content_of_models_py = f.read()
    assert expected == content_of_models_py


def test_correct_work_with_dash_simbols():
    ddl = """
    CREATE table "-arrays---2" (
        field_1                decimal(21)[] not null
    ,field_2              integer(61) array not null
    ,field_3              varchar array not null default '{"none"}'
    ,squares   integer[3][3] not null default '{1}'
    ,schedule        text[][]
    ,pay_by_quarter  integer[]
    ,pay_by_quarter_2  integer ARRAY[4]
    ,pay_by_quarter_3  integer ARRAY
    ) ;

"""
    result = create_models(ddl)
    expected = """from gino import Gino
from sqlalchemy.dialects.postgresql import ARRAY

db = Gino()


class Arrays2(db.Model):

    __tablename__ = '-arrays---2'

    field_1 = db.Column(ARRAY(db.Numeric(21)), nullable=False)
    field_2 = db.Column(ARRAY(db.Integer(61)), nullable=False)
    field_3 = db.Column(ARRAY(db.String()), nullable=False, server_default='{"none"}')
    squares = db.Column(ARRAY(db.Integer()), nullable=False, server_default='{1}')
    schedule = db.Column(ARRAY(db.Text()))
    pay_by_quarter = db.Column(ARRAY(db.Integer()))
    pay_by_quarter_2 = db.Column(ARRAY(db.Integer()))
    pay_by_quarter_3 = db.Column(ARRAY(db.Integer()))
"""
    assert expected == result["code"]


def test_support_uuid_and_schema_in_table_args():
    ddl = """
CREATE TABLE "prefix--schema-name"."table" (
  _id uuid PRIMARY KEY,
);
"""
    result = create_models(ddl)
    expected = """from gino import Gino
from sqlalchemy.dialects.postgresql import UUID

db = Gino(schema="prefix--schema-name")


class Table(db.Model):

    __tablename__ = 'table'

    _id = db.Column(UUID, primary_key=True)
"""
    assert expected == result["code"]


def test_schema_not_global():
    ddl = """
    CREATE TABLE "prefix--schema-name"."table" (
    _id uuid PRIMARY KEY,
    one_more_id int
    );
        create unique index table_pk on "prefix--schema-name"."table" (one_more_id) ;
        create index table_ix2 on "prefix--schema-name"."table" (_id) ;
    """
    result = create_models(ddl, schema_global=False)
    expected = """from gino import Gino
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy import Index

db = Gino()


class Table(db.Model):

    __tablename__ = 'table'

    _id = db.Column(UUID, primary_key=True)
    one_more_id = db.Column(db.Integer())

    __table_args__ = (
    UniqueConstraint(one_more_id, name='table_pk'),
    Index('table_ix2', _id),
    dict(schema="prefix--schema-name"))
"""
    assert expected == result["code"]


def test_foreign_key_from_alter():
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
    result = create_models(ddl, schema_global=False)
    expected = """from gino import Gino

db = Gino()


class Materials(db.Model):

    __tablename__ = 'materials'

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(), nullable=False)
    description = db.Column(db.String())
    link = db.Column(db.String())
    created_at = db.Column(db.TIMESTAMP())
    updated_at = db.Column(db.TIMESTAMP())


class MaterialAttachments(db.Model):

    __tablename__ = 'material_attachments'

    material_id = db.Column(db.Integer(), db.ForeignKey('materials.id'))
    attachment_id = db.Column(db.Integer(), db.ForeignKey('attachments.id'))


class Attachments(db.Model):

    __tablename__ = 'attachments'

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String())
    description = db.Column(db.String())
    created_at = db.Column(db.TIMESTAMP())
    updated_at = db.Column(db.TIMESTAMP())
"""
    assert expected == result["code"]


def test_foreign_key_from_column():
    ddl = """

    CREATE TABLE order_items (
        product_no integer REFERENCES products,
        order_id integer REFERENCES orders (id),
        type integer REFERENCES types (type_id),
        PRIMARY KEY (product_no, order_id)
    );

"""
    result = create_models(ddl, schema_global=False)["code"]
    expected = """from gino import Gino

db = Gino()


class OrderItems(db.Model):

    __tablename__ = 'order_items'

    product_no = db.Column(db.Integer(), db.ForeignKey('products.product_no'), primary_key=True)
    order_id = db.Column(db.Integer(), db.ForeignKey('orders.id'), primary_key=True)
    type = db.Column(db.Integer(), db.ForeignKey('types.type_id'))
"""
    assert expected == result


def test_foreign_key_on_delete_on_update():
    expected = """from gino import Gino

db = Gino()


class OrderItems(db.Model):

    __tablename__ = 'order_items'

    product_no = db.Column(db.Integer(), db.ForeignKey('products.product_no'), ondelete="RESTRICT", primary_key=True)
    order_id = db.Column(db.Integer(), db.ForeignKey('orders.order_id'), ondelete="CASCADE", primary_key=True)
    type = db.Column(db.Integer(), db.ForeignKey('types.type_id'), ondelete="RESTRICT", onupdate="CASCADE")
"""

    ddl = """
    CREATE TABLE order_items (
        product_no integer REFERENCES products ON DELETE RESTRICT,
        order_id integer REFERENCES orders ON DELETE CASCADE,
        type integer REFERENCES types (type_id) ON UPDATE CASCADE ON DELETE RESTRICT,
        PRIMARY KEY (product_no, order_id)
    );
    """
    result = create_models(ddl, schema_global=False)["code"]
    assert result == expected


def test_no_auto_snake_case():
    expected = """from gino import Gino

db = Gino()


class Merchants(db.Model):

    __tablename__ = 'merchants'

    id = db.Column(db.Integer(), primary_key=True)
    merchant_name = db.Column(db.String())


class Products(db.Model):

    __tablename__ = 'products'

    ID = db.Column(db.Integer(), primary_key=True)
    merchant_id = db.Column(db.Integer(), db.ForeignKey('merchants.id'), nullable=False)
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
    result = create_models(ddl, models_type="gino", no_auto_snake_case=True)["code"]
    assert expected == result
