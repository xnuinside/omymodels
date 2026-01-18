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

MaterialType = Enum(
    value='MaterialType',
    names=[
        ('article', 'article'),
        ('video', 'video')
    ]
)
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

ContentType = Enum(
    value='ContentType',
    names=[
        ('HTML', 'HTML'),
        ('MARKDOWN', 'MARKDOWN'),
        ('TEXT', 'TEXT')
    ]
)

Period = Enum(
    value='Period',
    names=[
        ('zero', 0),
        ('one', 1),
        ('two', 2)
    ]
)
"""
    assert expected == result

def test_enum_with_whitespace():
    ddl = """
    CREATE TYPE "enum_with_spaces" AS ENUM (
    'some value',
    'another value'
    );
    """
    result = create_models(ddl)["code"]
    expected = """from enum import Enum

EnumWithSpaces = Enum(
    value='EnumWithSpaces',
    names=[
        ('another value', 'another value'),
        ('some value', 'some value')
    ]
)
"""
    assert result == expected