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
    
    expected = """import datetime
from typing import Optional
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
    assert result == expected


def test_pydantic_with_arrays():
    expected = """from typing import List, Optional
from pydantic import BaseModel


class Arrays2(BaseModel):

    field_1: List[int]
    field_2: List[int]
    field_3: List[str]
    squares: List[int]
    schedule: Optional[List[str]]
    pay_by_quarter: Optional[List[int]]
    pay_by_quarter_2: Optional[List[int]]
    pay_by_quarter_3: Optional[List[int]]
"""
    ddl = """
    CREATE table arrays_2 (
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
    result = create_models(ddl, models_type="pydantic")['code']
    assert expected == result