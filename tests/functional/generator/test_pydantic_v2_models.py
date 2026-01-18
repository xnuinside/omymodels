from omymodels import create_models


def test_pydantic_v2_models_generator():
    """Test basic Pydantic v2 model generation with X | None syntax."""
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
    result = create_models(ddl, models_type="pydantic_v2")["code"]

    expected = """from __future__ import annotations

import datetime
from pydantic import BaseModel, Field


class UserHistory(BaseModel):

    runid: float | None = None
    job_id: float | None = None
    id: str = Field(max_length=100)
    user: str = Field(max_length=100)
    status: str = Field(max_length=10)
    event_time: datetime.datetime = datetime.datetime.now()
    comment: str = Field(default='none', max_length=1000)
"""
    assert result == expected


def test_pydantic_v2_with_arrays():
    """Test Pydantic v2 with array types using list[X] syntax."""
    expected = """from __future__ import annotations

from pydantic import BaseModel


class Arrays2(BaseModel):

    field_1: list[float]
    field_2: list[int]
    field_3: list[str] = '{"none"}'
    squares: list[int] = '{1}'
    schedule: list[str] | None = None
    pay_by_quarter: list[int] | None = None
    pay_by_quarter_2: list[int] | None = None
    pay_by_quarter_3: list[int] | None = None
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
    result = create_models(ddl, models_type="pydantic_v2")["code"]
    assert expected == result


def test_pydantic_v2_uuid():
    """Test Pydantic v2 with UUID type."""
    expected = """from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel


class Table(BaseModel):

    _id: UUID
"""
    ddl = """
CREATE TABLE "prefix--schema-name"."table" (
  _id uuid PRIMARY KEY,
);
"""
    result = create_models(ddl, models_type="pydantic_v2")
    assert expected == result["code"]


def test_pydantic_v2_enums():
    """Test Pydantic v2 with enum types."""
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
    result = create_models(ddl, models_type="pydantic_v2")["code"]

    # Verify key features of Pydantic v2 output
    assert "from __future__ import annotations" in result
    assert "from pydantic import BaseModel" in result
    assert "MaterialType = Enum(" in result
    assert "class Material(BaseModel):" in result
    # Pydantic v2 uses X | None syntax instead of Optional[X]
    assert "description: str | None = None" in result
    assert "type: MaterialType | None = None" in result
    # JSON types are dict | list in v2
    assert "additional_properties: dict | list | None = None" in result
    # Datetime defaults
    assert "created_at: datetime.datetime | None = datetime.datetime.now()" in result
    assert "updated_at: datetime.datetime | None = None" in result
    # No Optional import needed in v2
    assert "from typing import Optional" not in result
    # No Json import needed in v2
    assert "Json" not in result


def test_pydantic_v2_no_defaults():
    """Test Pydantic v2 with defaults_off option."""
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
    result = create_models(ddl, models_type="pydantic_v2", defaults_off=True)["code"]

    # Verify no defaults are added when defaults_off=True
    assert "from __future__ import annotations" in result
    assert "from pydantic import BaseModel" in result
    assert "class Material(BaseModel):" in result
    # Nullable fields should have X | None but no = None default
    assert "description: str | None\n" in result
    assert "type: MaterialType | None\n" in result
    assert "additional_properties: dict | list | None\n" in result
    assert "created_at: datetime.datetime | None\n" in result
    assert "updated_at: datetime.datetime | None\n" in result
    # Should NOT have any defaults
    assert "= None" not in result
    assert "= datetime.datetime.now()" not in result


def test_pydantic_v2_with_bytes():
    """Test Pydantic v2 with bytes type."""
    expected = """from __future__ import annotations

from pydantic import BaseModel


class User(BaseModel):

    avatar: bytes
"""

    ddl = """
CREATE TABLE "User" (
    "avatar" BINARY  NOT NULL
);
"""
    result = create_models(ddl, models_type="pydantic_v2")

    assert expected == result["code"]


def test_pydantic_v2_json_types():
    """Test Pydantic v2 uses dict | list for JSON types."""
    ddl = """
CREATE TABLE "config" (
    "id" SERIAL PRIMARY KEY,
    "settings" json NOT NULL,
    "metadata" jsonb
);
"""
    result = create_models(ddl, models_type="pydantic_v2")["code"]

    expected = """from __future__ import annotations

from pydantic import BaseModel


class Config(BaseModel):

    id: int
    settings: dict | list
    metadata: dict | list | None = None
"""
    assert expected == result


def test_pydantic_v2_all_nullable_fields():
    """Test Pydantic v2 with all nullable fields."""
    ddl = """
CREATE TABLE "optional_data" (
    "name" varchar NULL,
    "age" int NULL,
    "active" boolean NULL
);
"""
    result = create_models(ddl, models_type="pydantic_v2")["code"]

    expected = """from __future__ import annotations

from pydantic import BaseModel


class OptionalData(BaseModel):

    name: str | None = None
    age: int | None = None
    active: bool | None = None
"""
    assert expected == result


def test_pydantic_v2_varchar_max_length():
    """Test that VARCHAR(n) generates Field(max_length=n) in Pydantic v2.

    Regression test for issue #48.
    """
    ddl = """
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    bio TEXT
);
"""
    result = create_models(ddl, models_type="pydantic_v2")
    expected = """from __future__ import annotations

from pydantic import BaseModel, Field


class Users(BaseModel):

    id: int
    name: str = Field(max_length=100)
    email: str | None = Field(default=None, max_length=255)
    bio: str | None = None
"""
    assert expected == result["code"]


def test_pydantic_v2_char_max_length():
    """Test that CHAR(n) generates Field(max_length=n) in Pydantic v2.

    Regression test for issue #48.
    """
    ddl = """
CREATE TABLE codes (
    code CHAR(10) NOT NULL,
    description VARCHAR(200)
);
"""
    result = create_models(ddl, models_type="pydantic_v2")
    expected = """from __future__ import annotations

from pydantic import BaseModel, Field


class Codes(BaseModel):

    code: str = Field(max_length=10)
    description: str | None = Field(default=None, max_length=200)
"""
    assert expected == result["code"]
