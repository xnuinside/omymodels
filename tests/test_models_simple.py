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

    id = db.Column(db.Integer(), autoincrement=True, nullable=False, primary_key=True)
    name = db.Column(db.String())
    created_at = db.Column(db.TIMESTAMP())
    updated_at = db.Column(db.TIMESTAMP())
    country_code = db.Column(db.Integer())
    default_language = db.Column(db.Integer())


class Languages(db.Model):

    __tablename__ = 'languages'

    id = db.Column(db.Integer(), nullable=False, primary_key=True)
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


def test_ddl_with_defaults():
    ddl = """
    drop table if exists v2.task_requests ;
    CREATE table v2.task_requests (
        runid                decimal(21) not null
    ,job_id               decimal(21) not null
    ,object_id            varchar(100) not null default 'none'
    ,pipeline_id          varchar(100) not null default 'none'
    ,sequence             smallint not null
    ,processor_id         varchar(100) not null
    ,source_file          varchar(1000) not null default 'none'
    ,job_args             varchar array null
    ,request_time         timestamp not null default now()
    ,status               varchar(25) not null
    ,status_update_time   timestamp null default now()
    ) ;
    create unique index task_requests_pk on v2.task_requests (runid) ;

    """

    pass


def test_drop_does_not_break_anything():
    ddl = """
    drop table if exists v2.task_requests ;
    CREATE table v2.task_requests (
        runid                decimal(21) not null
    ,job_id               decimal(21) not null
    ,object_id            varchar(100) not null default 'none'
    ,pipeline_id          varchar(100) not null default 'none'
    ,sequence             smallint not null
    ,processor_id         varchar(100) not null
    ,source_file          varchar(1000) not null default 'none'
    ,job_args             varchar array null
    ,request_time         timestamp not null default now()
    ,status               varchar(25) not null
    ,status_update_time   timestamp null default now()
    ) ;
    create unique index task_requests_pk on v2.task_requests (runid) ;

    """
    pass


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
    expected = """
from sqlalchemy.dialects.postgresql import ARRAY
from gino import Gino

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


def test_support_uuid_and_schema_in_table_args():
    ddl = """
CREATE TABLE "prefix--schema-name"."table" (
  _id uuid PRIMARY KEY,
);
"""
    result = create_models(ddl)
    expected = """from sqlalchemy.dialects.postgresql import UUID
from gino import Gino

db = Gino(schema="prefix--schema-name")


class Table(db.Model):

    __tablename__ = 'table'

    _id = db.Column(UUID, nullable=False, primary_key=True)
"""
    assert expected == result['code']


