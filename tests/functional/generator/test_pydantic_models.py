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

    expected = """from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserHistory(BaseModel):
    runid: Optional[float]
    job_id: Optional[float]
    id: str
    user: str
    status: str
    event_time: datetime = datetime.now()
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
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel

MaterialType = Enum(
    value='MaterialType',
    names=[
        ('article', 'article'),
        ('video', 'video')
    ]
)


class Material(BaseModel):
    id: int
    title: str
    description: Optional[str]
    link: str
    type: Optional[MaterialType]
    additional_properties: Optional[Any]
    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime]
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
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel

MaterialType = Enum(
    value='MaterialType',
    names=[
        ('article', 'article'),
        ('video', 'video')
    ]
)


class Material(BaseModel):
    id: int
    title: str
    description: Optional[str]
    link: str
    type: Optional[MaterialType]
    additional_properties: Optional[Any]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
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


def test_mysql_blob_types():
    """Test that MySQL blob types are correctly mapped to bytes.

    Regression test for issue #62.
    """
    ddl = """
CREATE TABLE blob_test (
    col_tinyblob TINYBLOB,
    col_blob BLOB,
    col_mediumblob MEDIUMBLOB,
    col_longblob LONGBLOB
);
"""
    result = create_models(ddl, models_type="pydantic")
    expected = """from typing import Optional
from pydantic import BaseModel


class BlobTest(BaseModel):
    col_tinyblob: Optional[bytes]
    col_blob: Optional[bytes]
    col_mediumblob: Optional[bytes]
    col_longblob: Optional[bytes]
"""
    assert expected == result["code"]


def test_mysql_all_common_types():
    """Test comprehensive MySQL type support.

    Regression test for issue #62 - covers integer, decimal, temporal,
    text, and binary types.
    """
    ddl = """
CREATE TABLE all_types (
    -- Integer types
    col_tinyint TINYINT NOT NULL,
    col_smallint SMALLINT,
    col_mediumint MEDIUMINT,
    col_int INT,
    col_bigint BIGINT,

    -- Decimal types
    col_decimal DECIMAL(10,2),
    col_float FLOAT,
    col_double DOUBLE,

    -- Temporal types
    col_date DATE,
    col_datetime DATETIME,
    col_timestamp TIMESTAMP,
    col_time TIME,
    col_year YEAR,

    -- Text types
    col_char CHAR(10),
    col_varchar VARCHAR(255),
    col_tinytext TINYTEXT,
    col_text TEXT,
    col_mediumtext MEDIUMTEXT,
    col_longtext LONGTEXT,

    -- Binary types
    col_binary BINARY(10),
    col_varbinary VARBINARY(255),
    col_tinyblob TINYBLOB,
    col_blob BLOB,
    col_mediumblob MEDIUMBLOB,
    col_longblob LONGBLOB,

    -- JSON type
    col_json JSON
);
"""
    result = create_models(ddl, models_type="pydantic")

    # Verify key type mappings
    code = result["code"]
    assert "col_tinyint: int" in code
    assert "col_smallint: Optional[int]" in code
    assert "col_bigint: Optional[int]" in code
    assert "col_decimal: Optional[float]" in code
    assert "col_float: Optional[float]" in code
    assert "col_double: Optional[float]" in code
    assert "col_date: Optional[date]" in code
    assert "col_datetime: Optional[datetime]" in code
    assert "col_timestamp: Optional[datetime]" in code
    assert "col_time: Optional[time]" in code
    assert "col_year: Optional[int]" in code
    assert "col_char: Optional[str]" in code
    assert "col_varchar: Optional[str]" in code
    assert "col_text: Optional[str]" in code
    assert "col_binary: Optional[bytes]" in code
    assert "col_varbinary: Optional[bytes]" in code
    assert "col_tinyblob: Optional[bytes]" in code
    assert "col_blob: Optional[bytes]" in code
    assert "col_mediumblob: Optional[bytes]" in code
    assert "col_longblob: Optional[bytes]" in code
    assert "col_json: Optional[Any]" in code


def test_mysql_default_null():
    """Test that DEFAULT NULL is handled correctly for temporal types.

    Regression test for issue #62.
    """
    ddl = """
CREATE TABLE test_defaults (
    col_date DATE DEFAULT NULL,
    col_datetime DATETIME DEFAULT NULL,
    col_timestamp TIMESTAMP DEFAULT NULL
);
"""
    result = create_models(ddl, models_type="pydantic")
    expected = """from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


class TestDefaults(BaseModel):
    col_date: Optional[date]
    col_datetime: Optional[datetime]
    col_timestamp: Optional[datetime]
"""
    assert expected == result["code"]
