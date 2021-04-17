from omymodels import create_models


def test_dataclasses():
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
    result = create_models(ddl, schema_global=False, models_type='dataclass')
    expected = """from typing import List
from dataclasses import dataclass


@dataclass
class Arrays2:

    field_1: List[int]
    field_2: List[int]
    field_3: List[str] = '{"none"}'
    squares: List[int] = '{1}'
    schedule: List[str] = None
    pay_by_quarter: List[int] = None
    pay_by_quarter_2: List[int] = None
    pay_by_quarter_3: List[int] = None
"""
    
    assert expected == result['code']