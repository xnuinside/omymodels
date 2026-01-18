"""Integration tests for SQLModel generation.

These tests verify that generated SQLModel code is valid and works correctly.
The code is pre-generated (as users would generate and commit to their repos).
"""

import os
import sys
import uuid

import pytest

try:
    from sqlmodel import SQLModel
    HAS_SQLMODEL = True
except ImportError:
    HAS_SQLMODEL = False

pytestmark = [
    pytest.mark.skipif(
        not HAS_SQLMODEL,
        reason="SQLModel is not installed"
    ),
    pytest.mark.skipif(
        sys.version_info < (3, 10),
        reason="SQLModel tests require Python 3.10+ for type syntax"
    ),
]


def get_basic_model_code(table_suffix: str) -> str:
    """Generate basic model code with unique table name."""
    return f'''
from typing import Optional
from sqlmodel import SQLModel, Field


class Users{table_suffix}(SQLModel, table=True):
    __tablename__ = 'users_{table_suffix}'

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    name: Optional[str] = None
    is_active: Optional[bool] = None
'''


def get_multiple_tables_code(table_suffix: str) -> str:
    """Generate multiple tables code with unique table names."""
    return f'''
from typing import Optional
from sqlmodel import SQLModel, Field


class Users{table_suffix}(SQLModel, table=True):
    __tablename__ = 'users_{table_suffix}'

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


class Posts{table_suffix}(SQLModel, table=True):
    __tablename__ = 'posts_{table_suffix}'

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    title: str
'''


def get_nullable_fields_code(table_suffix: str) -> str:
    """Generate nullable fields code with unique table name."""
    return f'''
from typing import Optional
from sqlmodel import SQLModel, Field


class Config{table_suffix}(SQLModel, table=True):
    __tablename__ = 'config_{table_suffix}'

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    max_retries: Optional[int] = None
'''


def test_sqlmodel_basic_model_is_valid(load_generated_code) -> None:
    """Integration test: verify generated SQLModel models are valid."""
    suffix = uuid.uuid4().hex[:8]
    code = get_basic_model_code(suffix)
    module = load_generated_code(code)

    class_name = f"Users{suffix}"

    # Verify model class exists
    assert hasattr(module, class_name)

    model_class = getattr(module, class_name)

    # Check the model has correct __tablename__
    assert model_class.__tablename__ == f"users_{suffix}"

    # Check it's a SQLModel
    assert issubclass(model_class, SQLModel)

    os.remove(os.path.abspath(module.__file__))


def test_sqlmodel_create_instance(load_generated_code) -> None:
    """Integration test: verify SQLModel instances can be created."""
    suffix = uuid.uuid4().hex[:8]
    code = get_basic_model_code(suffix)
    module = load_generated_code(code)

    model_class = getattr(module, f"Users{suffix}")

    # Create instance
    user = model_class(id=1, email="test@example.com", name="Test")
    assert user.id == 1
    assert user.email == "test@example.com"
    assert user.name == "Test"

    os.remove(os.path.abspath(module.__file__))


def test_sqlmodel_with_nullable_fields(load_generated_code) -> None:
    """Integration test: verify nullable fields work correctly."""
    suffix = uuid.uuid4().hex[:8]
    code = get_nullable_fields_code(suffix)
    module = load_generated_code(code)

    model_class = getattr(module, f"Config{suffix}")

    # Create instance with only required fields
    config = model_class(id=1, name="Test")
    assert config.id == 1
    assert config.name == "Test"
    assert config.description is None
    assert config.max_retries is None

    os.remove(os.path.abspath(module.__file__))


def test_sqlmodel_multiple_tables(load_generated_code) -> None:
    """Integration test: verify multiple SQLModel tables generate correctly."""
    suffix = uuid.uuid4().hex[:8]
    code = get_multiple_tables_code(suffix)
    module = load_generated_code(code)

    users_class = getattr(module, f"Users{suffix}")
    posts_class = getattr(module, f"Posts{suffix}")

    # Verify both models are SQLModel subclasses
    assert issubclass(users_class, SQLModel)
    assert issubclass(posts_class, SQLModel)

    # Create instances
    user = users_class(id=1, name="Test")
    post = posts_class(id=1, user_id=1, title="Hello")

    assert user.name == "Test"
    assert post.title == "Hello"

    os.remove(os.path.abspath(module.__file__))
