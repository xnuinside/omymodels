import os
from omymodels import create_gino_models


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
    assert expected == create_gino_models(ddl=ddl, dump=False)
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    models = os.path.join(tests_dir, 'test_models.py')
    ddl_path = os.path.join(tests_dir, 'test_two_tables.sql')
    create_gino_models(ddl_path=ddl_path, dump_path=models)
    with open(models, 'r') as f:
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