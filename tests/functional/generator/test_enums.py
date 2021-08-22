from omymodels import create_models


def test_enums_gino():
    expected = """from gino import Gino
from enum import Enum

db = Gino(schema="schema--notification")


class ContentType(str, Enum):

    HTML = 'HTML'
    MARKDOWN = 'MARKDOWN'
    TEXT = 'TEXT'
    

class Notification(db.Model):

    __tablename__ = 'notification'

    content_type = db.Column(db.Enum(ContentType))
"""

    ddl = """
CREATE TYPE "schema--notification"."ContentType" AS
 ENUM ('TEXT','MARKDOWN','HTML');
CREATE TABLE "schema--notification"."notification" (
    content_type "schema--notification"."ContentType"
);
"""
    result = create_models(ddl)
    assert result["code"] == expected


def test_pydantic_models():
    ddl = """
    CREATE TYPE "schema--notification"."ContentType" AS
    ENUM ('TEXT','MARKDOWN','HTML');

    CREATE TYPE "schema--notification"."Period" AS
    ENUM (0, 1, 2);

    CREATE TABLE "schema--notification"."notification" (
        content_type "schema--notification"."ContentType",
        period "schema--notification"."Period"
    );
    """
    result = create_models(ddl, models_type="pydantic")
    expected = """from enum import Enum, IntEnum
from typing import Optional
from pydantic import BaseModel


class ContentType(str, Enum):

    HTML = 'HTML'
    MARKDOWN = 'MARKDOWN'
    TEXT = 'TEXT'
    

class Period(IntEnum):

    zero = 0
    one = 1
    two = 2
    

class Notification(BaseModel):

    content_type: Optional[ContentType]
    period: Optional[Period]
"""
    assert expected == result["code"]


def test_enum_works_with_lower_case():
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
    result = create_models(ddl, schema_global=False)
    expected = """from gino import Gino
from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON

db = Gino()


class MaterialType(str, Enum):

    article = 'article'
    video = 'video'
    

class Material(db.Model):

    __tablename__ = 'material'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text())
    link = db.Column(db.String(), nullable=False)
    type = db.Column(db.Enum(MaterialType))
    additional_properties = db.Column(JSON())
    created_at = db.Column(db.TIMESTAMP(), server_default=func.now())
    updated_at = db.Column(db.TIMESTAMP())
"""
    assert result["code"] == expected
