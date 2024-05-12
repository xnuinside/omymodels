from omymodels import create_models


def test_with_enums():
    expected = """import datetime
import decimal
from typing import Optional
from sqlmodel import Field, SQLModel
from enum import Enum
import sqlalchemy as sa
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON
from pydantic import Json, UUID4


class MaterialType(str, Enum):

    article = 'article'
    video = 'video'
    

class Material(SQLModel, table=True):

    __tablename__ = 'material'

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = Field(sa_type=sa.Text())
    link: str
    type: Optional[MaterialType] = Field(sa_type=sa.Enum(MaterialType))
    additional_properties: Optional[Json] = Field(sa_column_kwargs={'server_default': '{"key": "value"}'}, sa_type=JSON())
    created_at: Optional[datetime.datetime] = Field(sa_column_kwargs={'server_default': func.now()})
    updated_at: Optional[datetime.datetime]
"""  # noqa: E501
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
    result = create_models(ddl, models_type="sqlmodel")
    assert expected == result["code"]


def test_foreign_keys():
    expected = """import datetime
import decimal
from typing import Optional
from sqlmodel import Field, SQLModel


class Materials(SQLModel, table=True):

    __tablename__ = 'materials'

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str]
    link: Optional[str]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class MaterialAttachments(SQLModel, table=True):

    __tablename__ = 'material_attachments'

    material_id: Optional[int] = Field(foreign_key='materials.id')
    attachment_id: Optional[int] = Field(foreign_key='attachments.id')


class Attachments(SQLModel, table=True):

    __tablename__ = 'attachments'

    id: Optional[int] = Field(default=None, primary_key=True)
    title: Optional[str]
    description: Optional[str]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
"""
    ddl = """

  CREATE TABLE "materials" (
  "id" int PRIMARY KEY,
  "title" varchar NOT NULL,
  "description" varchar,
  "link" varchar,
  "created_at" timestamp,
  "updated_at" timestamp
  );

  CREATE TABLE "material_attachments" (
  "material_id" int,
  "attachment_id" int
  );

  CREATE TABLE "attachments" (
  "id" int PRIMARY KEY,
  "title" varchar,
  "description" varchar,
  "created_at" timestamp,
  "updated_at" timestamp
  );


  ALTER TABLE "material_attachments" ADD FOREIGN KEY ("material_id") REFERENCES "materials" ("id");

  ALTER TABLE "material_attachments" ADD FOREIGN KEY ("attachment_id") REFERENCES "attachments" ("id");

  """
    result = create_models(ddl, models_type="sqlmodel")["code"]
    assert result == expected


def test_foreign_keys_defined_inline():
    """
    This should be the same output as test_foreign_keys, but with a slightly
    different, yet valid input DDL.
    """
    expected = """import datetime
import decimal
from typing import Optional
from sqlmodel import Field, SQLModel


class Materials(SQLModel, table=True):

    __tablename__ = 'materials'

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str]
    link: Optional[str]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class MaterialAttachments(SQLModel, table=True):

    __tablename__ = 'material_attachments'

    material_id: Optional[int] = Field(foreign_key='materials.id')
    attachment_id: Optional[int] = Field(foreign_key='attachments.id')


class Attachments(SQLModel, table=True):

    __tablename__ = 'attachments'

    id: Optional[int] = Field(default=None, primary_key=True)
    title: Optional[str]
    description: Optional[str]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
"""
    ddl = """

  CREATE TABLE "materials" (
  "id" int PRIMARY KEY,
  "title" varchar NOT NULL,
  "description" varchar,
  "link" varchar,
  "created_at" timestamp,
  "updated_at" timestamp
  );

  CREATE TABLE "material_attachments" (
  "material_id" int,
  "attachment_id" int,
  CONSTRAINT "material_id_ibfk" FOREIGN KEY ("material_id") REFERENCES "materials" ("id"),
  CONSTRAINT "attachment_id_ibfk" FOREIGN KEY ("attachment_id") REFERENCES "attachments" ("id")
  );

  CREATE TABLE "attachments" (
  "id" int PRIMARY KEY,
  "title" varchar,
  "description" varchar,
  "created_at" timestamp,
  "updated_at" timestamp
  );
  """
    result = create_models(ddl, models_type="sqlmodel")["code"]
    assert result == expected


def test_multi_col_pk_and_fk():
    """
    This should test that we can properly setup tables with compound PRIMARY and
    FOREIGN keys.
    """
    expected = """import datetime
import decimal
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy.sql import func


class Complexpk(SQLModel, table=True):

    __tablename__ = 'complexpk'

    complex_id: Optional[int] = Field(default=None, primary_key=True)
    date_part: Optional[datetime.datetime] = Field(sa_column_kwargs={'server_default': func.now()}, default=None, primary_key=True)
    title: str
    description: Optional[str]


class LinkedTo(SQLModel, table=True):

    __tablename__ = 'linked_to'

    id: Optional[int] = Field(default=None, primary_key=True)
    complexpk_complex_id: Optional[int] = Field(foreign_key='complexpk.complex_id')
    complexpk_date_part: Optional[int] = Field(foreign_key='complexpk.date_part')
    comment: Optional[str]
"""  # noqa: E501

    ddl = """

  CREATE TABLE "complexpk" (
  "complex_id" int unsigned NOT NULL,
  "date_part" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "title" varchar NOT NULL,
  "description" varchar,
  PRIMARY KEY ("complex_id","date_part")
  );

  CREATE TABLE "linked_to" (
  "id" int PRIMARY KEY,
  "complexpk_complex_id" int,
  "complexpk_date_part" int,
  "comment" varchar,
  CONSTRAINT "id_date_part_ibfk" FOREIGN KEY ("complexpk_complex_id", "complexpk_date_part")
    REFERENCES "complexpk" ("complex_id", "date_part")
  );

  """
    result = create_models(ddl, models_type="sqlmodel")["code"]
    assert result == expected


def test_upper_name_produces_the_same_result():
    expected = """import datetime
import decimal
from typing import Optional
from sqlmodel import Field, SQLModel
from enum import Enum
import sqlalchemy as sa
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON
from pydantic import Json, UUID4


class MaterialType(str, Enum):

    article = 'article'
    video = 'video'
    

class Material(SQLModel, table=True):

    __tablename__ = 'material'

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = Field(sa_type=sa.Text())
    link: str
    type: Optional[MaterialType] = Field(sa_type=sa.Enum(MaterialType))
    additional_properties: Optional[Json] = Field(sa_column_kwargs={'server_default': '{"key": "value"}'}, sa_type=JSON())
    created_at: Optional[datetime.datetime] = Field(sa_column_kwargs={'server_default': func.now()})
    updated_at: Optional[datetime.datetime]
"""  # noqa: E501
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
  "created_at" timestamp DEFAULT (NOW()),
  "updated_at" timestamp
);
"""
    result = create_models(ddl, models_type="sqlmodel")
    assert expected == result["code"]


def test_foreign_keys_in_different_schema():
    expected = """import datetime
import decimal
from typing import Optional
from sqlmodel import Field, SQLModel


class Table1(SQLModel, table=True):

    __tablename__ = 'table1'

    id: Optional[int] = Field(default=None, primary_key=True)
    reference_to_table_in_another_schema: int = Field(foreign_key='schema2.table2.id')

    __table_args__ = (
                
    dict(schema="schema1"),
            )



class Table2(SQLModel, table=True):

    __tablename__ = 'table2'

    id: Optional[int] = Field(default=None, primary_key=True)

    __table_args__ = (
                
    dict(schema="schema2"),
            )

"""
    ddl = """
CREATE SCHEMA "schema1";

CREATE SCHEMA "schema2";

CREATE TABLE "schema1"."table1" (
  "id" int PRIMARY KEY,
  "reference_to_table_in_another_schema" int NOT NULL
);

CREATE TABLE "schema2"."table2" (
  "id" int PRIMARY KEY
);

ALTER TABLE "schema1"."table1" ADD FOREIGN KEY
("reference_to_table_in_another_schema") REFERENCES "schema2"."table2" ("id");
"""
    result = create_models(ddl, schema_global=False, models_type="sqlmodel")["code"]
    assert result == expected


def test_sqlmodel_varying():
    ddl = """
    CREATE TABLE qwe (
        id integer NOT NULL,
        name character varying(255),
    );
    """
    result = create_models(ddl, models_type="sqlmodel")["code"]
    expected = """import datetime
import decimal
from typing import Optional
from sqlmodel import Field, SQLModel


class Qwe(SQLModel, table=True):

    __tablename__ = 'qwe'

    id: int
    name: Optional[str]
"""
    assert expected == result
