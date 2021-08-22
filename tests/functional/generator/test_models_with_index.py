from omymodels import create_models


def test_model_with_one_index():
    ddl = """CREATE table schema_name.task_requests (
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
    create unique index task_requests_pk on schema_name.task_requests (runid) ;"""
    result = create_models(ddl, models_type="gino")["code"]
    expected = """from gino import Gino
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.schema import UniqueConstraint

db = Gino(schema="schema_name")


class TaskRequests(db.Model):

    __tablename__ = 'task_requests'

    runid = db.Column(db.Numeric(21), nullable=False)
    job_id = db.Column(db.Numeric(21), nullable=False)
    object_id = db.Column(db.String(100), nullable=False, server_default='none')
    pipeline_id = db.Column(db.String(100), nullable=False, server_default='none')
    sequence = db.Column(db.SmallInteger(), nullable=False)
    processor_id = db.Column(db.String(100), nullable=False)
    source_file = db.Column(db.String(1000), nullable=False, server_default='none')
    job_args = db.Column(ARRAY(db.String()))
    request_time = db.Column(db.TIMESTAMP(), nullable=False, server_default=func.now())
    status = db.Column(db.String(25), nullable=False)
    status_update_time = db.Column(db.TIMESTAMP(), server_default=func.now())

    __table_args__ = (
    UniqueConstraint(runid, name='task_requests_pk'))
"""  # noqa: W293
    assert expected == result
