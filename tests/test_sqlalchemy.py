from omymodels import create_models


def test_with_enums():
    expected = """from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class MaterialType(Enum):

    article = 'article'
    video = 'video'


class Material(Base):

    __tablename__ = 'material'

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    title = sa.Column(sa.String(), nullable=False)
    description = sa.Column(sa.Text())
    link = sa.Column(sa.String(), nullable=False)
    type = sa.Column(sa.Enum(MaterialType))
    additional_properties = sa.Column(JSON(), server_default='{"key": "value"}')
    created_at = sa.Column(sa.TIMESTAMP(), server_default=func.now())
    updated_at = sa.Column(sa.TIMESTAMP())
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
    result = create_models(ddl, models_type='sqlalchemy')
    assert expected == result['code']
