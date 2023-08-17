from omymodels import create_models


def test_enum_only():
    ddl = """
    CREATE TYPE "material_type" AS ENUM (
    'video',
    'article'
    );
    """
    result = create_models(ddl)["code"]

    expected = """from enum import Enum


class MaterialType(str, Enum):

    article = 'article'
    video = 'video'
    """

    assert result == expected


def test_enum_models():
    ddl = """
    CREATE TYPE "schema--notification"."ContentType" AS
    ENUM ('TEXT','MARKDOWN','HTML');

    CREATE TYPE "schema--notification"."Period" AS
    ENUM (0, 1, 2);
    """
    result = create_models(ddl)["code"]
    expected = """from enum import Enum, IntEnum


class ContentType(str, Enum):

    HTML = 'HTML'
    MARKDOWN = 'MARKDOWN'
    TEXT = 'TEXT'
    

class Period(IntEnum):

    zero = 0
    one = 1
    two = 2
    """
    assert expected == result
