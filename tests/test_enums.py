from omymodels import create_models


def test_enums_gino():
    expected = """from enum import Enum
from gino import Gino

db = Gino(schema="schema--notification")


class ContentType(Enum):

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
    result = create_models(ddl, models_type='pydantic')
    expected = """
    from enum import IntEnum,Enum
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