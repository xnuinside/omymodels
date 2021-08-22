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
    result = create_models(ddl, models_type="dataclass")
    expected = """from typing import List
from dataclasses import dataclass


@dataclass
class Arrays2:

    field_1: List[float]
    field_2: List[int]
    field_3: List[str] = '{"none"}'
    squares: List[int] = '{1}'
    schedule: List[str] = None
    pay_by_quarter: List[int] = None
    pay_by_quarter_2: List[int] = None
    pay_by_quarter_3: List[int] = None
"""

    assert expected == result["code"]


def test_defaults_datetime():
    ddl = """
CREATE table user_history (
     runid                 decimal(21) null
    ,job_id                decimal(21)  null
    ,id                    varchar(100) not null
    ,user              varchar(100) not null
    ,status                varchar(10) not null
    ,event_time            timestamp not null default now()
    ,comment           varchar(1000) not null default 'none'
    ) ;

"""
    result = create_models(ddl, models_type="dataclass")
    expected = """import datetime
from dataclasses import dataclass, field


@dataclass
class UserHistory:

    id: str
    user: str
    status: str
    runid: float = None
    job_id: float = None
    event_time: datetime.datetime = field(default_factory=datetime.datetime.now)
    comment: str = 'none'
"""
    assert expected == result["code"]


def test_enums_in_dataclasses():
    expected = """from enum import Enum
import datetime
from typing import Union
from dataclasses import dataclass, field


class MaterialType(str, Enum):

    article = 'article'
    video = 'video'
    

@dataclass
class Material:

    id: int
    title: str
    link: str
    description: str = None
    type: MaterialType = None
    additional_properties: Union[dict, list] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = None
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
  "additional_properties" json,
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp
);
"""
    result = create_models(ddl, models_type="dataclass")["code"]
    assert expected == result


def test_defaults_off():
    expected = """from enum import Enum
import datetime
from typing import Union
from dataclasses import dataclass, field


class MaterialType(str, Enum):

    article = 'article'
    video = 'video'
    

@dataclass
class Material:

    id: int
    title: str
    description: str
    link: str
    type: MaterialType
    additional_properties: Union[dict, list]
    created_at: datetime.datetime
    updated_at: datetime.datetime
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
    result = create_models(ddl, models_type="dataclass", defaults_off=True)
    assert expected == result["code"]


def test_upper_now_produces_same_result():
    expected = """from enum import Enum
import datetime
from typing import Union
from dataclasses import dataclass, field


class MaterialType(str, Enum):

    article = 'article'
    video = 'video'
    

@dataclass
class Material:

    id: int
    title: str
    link: str
    description: str = None
    type: MaterialType = None
    additional_properties: Union[dict, list] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = None
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
  "additional_properties" json,
  "created_at" timestamp DEFAULT (NOW()),
  "updated_at" timestamp
);
"""
    result = create_models(ddl, models_type="dataclass")["code"]
    assert expected == result
