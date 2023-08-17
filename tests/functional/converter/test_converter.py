import pytest
from helpers import generate_params_for_converter

from omymodels import convert_models


def test_convert_models():
    models_from = """

    class MaterialType(str, Enum):

        article = "article"
        video = "video"


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

    result = convert_models(models_from)
    expected = """from gino import Gino
from enum import Enum
from sqlalchemy.dialects.postgresql import JSON

db = Gino()


class MaterialType(str, Enum):

    article = article
    video = video
    

class Material(db.Model):

    __tablename__ = 'materials'

    id = db.Column(db.Integer())
    title = db.Column(db.String())
    description = db.Column(db.String())
    link = db.Column(db.String())
    type = db.Column(db.Enum(MaterialType))
    additional_properties = db.Column(JSON())
    created_at = db.Column(db.DateTime())
    updated_at = db.Column(db.DateTime())
"""
    assert result == expected


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
params = generate_params_for_converter(ddl)


@pytest.mark.skip
@pytest.mark.parametrize(
    "base_model_type,target_model_type,base_model_code,target_model_code", params
)
def test_convert_models_params(
    base_model_type: str,
    target_model_type: str,
    base_model_code: str,
    target_model_code: str,
):
    assert (
        convert_models(base_model_code, models_type=target_model_type)
        == target_model_code
    )


def test_from_sqlalchemy_to_gino():
    expected = """from gino import Gino
from enum import Enum
from sqlalchemy.dialects.postgresql import JSON

db = Gino()


class MaterialType(str, Enum):

    article = 'article'
    video = 'video'
    

class Material(db.Model):

    __tablename__ = 'materials'

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String())
    description = db.Column(db.Text())
    link = db.Column(db.String())
    type = db.Column(db.Enum(MaterialType))
    additional_properties = db.Column(JSON())
    created_at = db.Column(db.TIMESTAMP())
    updated_at = db.Column(db.TIMESTAMP())
"""
    models_from = """
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON


Base = declarative_base()


class MaterialType(str, Enum):

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
    # result = create_models(ddl)['code']
    result = convert_models(models_from, models_type="gino")
    assert expected == result


def test_from_sqlalchemy_to_pydantic():
    expected = """from enum import Enum
import datetime
from typing import Optional
from pydantic import BaseModel, Json


class MaterialType(str, Enum):

    article = 'article'
    video = 'video'
    

class Material(BaseModel):

    id: Optional[int]
    title: Optional[str]
    description: Optional[str]
    link: Optional[str]
    type: Optional[MaterialType]
    additional_properties: Optional[Json]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
"""

    models_from = """
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON


Base = declarative_base()


class MaterialType(str, Enum):

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
    result = convert_models(models_from, models_type="pydantic")
    assert expected == result
