from omymodels import create_models


def test_unique_and_normal_index():
    ddl = """
    drop table if exists schema_name.approver_history ;
    CREATE table schema_name.approver_history (
        runid                 decimal(21) not null
    ,job_id                decimal(21) not null
    ,id                    varchar(100) not null -- group_id or role_id
    ,approver              varchar(100) not null
    ,status                varchar(10) not null
    ,event_time            timestamp not null default now()
    ,deny_reason           varchar(1000) not null default 'none'
    ) ;
    create unique index approver_history_pk on schema_name.approver_history (runid) ;
    create index approver_history_ix2 on schema_name.approver_history (job_id) ;
    create index approver_history_ix3 on schema_name.approver_history (id) ;"""
    expected = """from gino import Gino
from sqlalchemy.sql import func
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy import Index

db = Gino(schema="schema_name")


class ApproverHistory(db.Model):

    __tablename__ = 'approver_history'

    runid = db.Column(db.Numeric(21), nullable=False)
    job_id = db.Column(db.Numeric(21), nullable=False)
    id = db.Column(db.String(100), nullable=False)
    approver = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    event_time = db.Column(db.TIMESTAMP(), nullable=False, server_default=func.now())
    deny_reason = db.Column(db.String(1000), nullable=False, server_default='none')

    __table_args__ = (
    UniqueConstraint(runid, name='approver_history_pk'),
    Index('approver_history_ix2', job_id),
    Index('approver_history_ix3', id))
"""
    gino_models = create_models(ddl=ddl, dump=False)["code"]
    assert expected == gino_models
