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
    result = create_models(ddl, models_type="pydantic")["code"]

    expected = """import datetime
from typing import Optional
from pydantic import BaseModel


class UserHistory(BaseModel):

    runid: Optional[float]
    job_id: Optional[float]
    id: str
    user: str
    status: str
    event_time: datetime.datetime = datetime.datetime.now()
    comment: str = 'none'
"""
    assert result == expected


def test_pydantic_with_arrays():
    expected = """from typing import List, Optional
from pydantic import BaseModel


class Arrays2(BaseModel):

    field_1: List[float]
    field_2: List[int]
    field_3: List[str] = '{"none"}'
    squares: List[int] = '{1}'
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
    result = create_models(ddl, models_type="pydantic")["code"]
    assert expected == result


def test_pydantic_uuid():
    expected = """from uuid import UUID
from pydantic import BaseModel


class Table(BaseModel):

    _id: UUID
"""
    ddl = """
CREATE TABLE "prefix--schema-name"."table" (
  _id uuid PRIMARY KEY,
);
"""
    result = create_models(ddl, models_type="pydantic")
    assert expected == result["code"]


def test_enums_lower_case_names_works():
    expected = """from enum import Enum
import datetime
from typing import Optional
from pydantic import BaseModel, Json


class MaterialType(str, Enum):

    article = 'article'
    video = 'video'
    

class Material(BaseModel):

    id: int
    title: str
    description: Optional[str]
    link: str
    type: Optional[MaterialType]
    additional_properties: Optional[Json]
    created_at: Optional[datetime.datetime] = datetime.datetime.now()
    updated_at: Optional[datetime.datetime]
"""
    from omymodels import create_models

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
    result = create_models(ddl, models_type="pydantic")["code"]
    assert result == expected


def test_no_defaults():
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
    result = create_models(ddl, models_type="pydantic", defaults_off=True)["code"]
    expected = """from enum import Enum
import datetime
from typing import Optional
from pydantic import BaseModel, Json


class MaterialType(str, Enum):

    article = 'article'
    video = 'video'
    

class Material(BaseModel):

    id: int
    title: str
    description: Optional[str]
    link: str
    type: Optional[MaterialType]
    additional_properties: Optional[Json]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
"""
    assert expected == result


def test_pydantic_with_bytes():
    expected = """from pydantic import BaseModel


class User(BaseModel):

    avatar: bytes
"""

    ddl = """
CREATE TABLE "User" (
    "avatar" BINARY  NOT NULL
);
"""
    result = create_models(ddl, models_type="pydantic")

    assert expected == result["code"]
