from omymodels import create_models


def test_pydantic_models_generator():
    
    ddl = """
CREATE table user_history (
        runid                 decimal(21) null
    ,job_id                decimal(21)  null
    ,id                    varchar(100) not null -- group_id or role_id
    ,user              varchar(100) not null
    ,status                varchar(10) not null
    ,event_time            timestamp not null default now()
    ,comment           varchar(1000) not null default 'none'
    ) ;


"""
    result = create_models(ddl, models_type='pydantic')['code']
    
    expected = """
import datetime
from typing import Optional, Optional
from pydantic import BaseModel


class UserHistory(BaseModel):

    runid: Optional[int]
    job_id: Optional[int]
    id: str
    user: str
    status: str
    event_time: datetime.datetime
    comment: str   
    
"""
