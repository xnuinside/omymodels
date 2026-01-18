"""Integration tests for Pydal to SQLAlchemy model conversion."""

import os

import pytest

from omymodels import convert_models

try:
    import sqlalchemy  # noqa: F401
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False

pytestmark = pytest.mark.skipif(
    not HAS_SQLALCHEMY,
    reason="SQLAlchemy is not installed"
)


def test_pydal_to_sqlalchemy_valid_model(load_generated_code) -> None:
    """Integration test: verify converted Pydal models are valid SQLAlchemy."""
    # Using "id" type which is Pydal's primary key type
    pydal_code = (
        '''db.define_table("users", Field("id", "id"), '''
        '''Field("name", "string"), Field("email", "string"))'''
    )

    result = convert_models(pydal_code, models_type="sqlalchemy")

    module = load_generated_code(result)

    # Verify Base class exists
    assert hasattr(module, "Base")

    # Verify model class exists
    assert hasattr(module, "User")

    # Check the model has correct __tablename__
    assert module.User.__tablename__ == "users"

    # Verify columns exist in __table__.columns
    column_names = [c.name for c in module.User.__table__.columns]
    assert "id" in column_names
    assert "name" in column_names
    assert "email" in column_names

    # Verify id is a primary key
    assert module.User.__table__.columns["id"].primary_key

    os.remove(os.path.abspath(module.__file__))


def test_pydal_to_sqlalchemy_foreign_key(load_generated_code) -> None:
    """Integration test: verify Pydal references become valid SQLAlchemy ForeignKeys."""
    pydal_code = '''db.define_table("users", Field("id", "id"), Field("name", "string"))

db.define_table("posts", Field("id", "id"), Field("title", "string"), \
Field("user_id", "reference users"))'''

    result = convert_models(pydal_code, models_type="sqlalchemy")

    module = load_generated_code(result)

    # Verify both models exist
    assert hasattr(module, "User")
    assert hasattr(module, "Post")

    # Check foreign key exists on posts
    user_id_col = module.Post.__table__.columns["user_id"]
    assert len(user_id_col.foreign_keys) == 1

    # Verify foreign key references the correct table
    fk = list(user_id_col.foreign_keys)[0]
    assert str(fk.column) == "users.id"

    os.remove(os.path.abspath(module.__file__))


def test_pydal_to_sqlalchemy_multiple_types(load_generated_code) -> None:
    """Integration test: verify various Pydal types convert correctly."""
    # Include id field for primary key
    pydal_code = '''db.define_table("test_types", Field("id", "id"),
                Field("col_string", "string"),
                Field("col_text", "text"),
                Field("col_integer", "integer"),
                Field("col_boolean", "boolean"),
                Field("col_float", "float"))'''

    result = convert_models(pydal_code, models_type="sqlalchemy")

    module = load_generated_code(result)

    # Verify model exists
    assert hasattr(module, "TestType")

    # Verify all columns exist and have correct types
    table = module.TestType.__table__

    from sqlalchemy import String, Text, Integer, Boolean, Float

    assert isinstance(table.columns["col_string"].type, String)
    assert isinstance(table.columns["col_text"].type, Text)
    assert isinstance(table.columns["col_integer"].type, Integer)
    assert isinstance(table.columns["col_boolean"].type, Boolean)
    assert isinstance(table.columns["col_float"].type, Float)

    os.remove(os.path.abspath(module.__file__))


def test_pydal_to_sqlalchemy_v2_valid_model(load_generated_code) -> None:
    """Integration test: verify converted Pydal models are valid SQLAlchemy v2."""
    pydal_code = '''db.define_table("users", Field("id", "id"), Field("name", "string"))'''

    result = convert_models(pydal_code, models_type="sqlalchemy_v2")

    module = load_generated_code(result)

    # Verify Base class exists with DeclarativeBase pattern
    assert hasattr(module, "Base")

    # Verify model class exists
    assert hasattr(module, "User")

    # Check the model has correct __tablename__
    assert module.User.__tablename__ == "users"

    os.remove(os.path.abspath(module.__file__))


def test_pydal_to_pydantic_valid_model(load_generated_code) -> None:
    """Integration test: verify converted Pydal models are valid Pydantic."""
    pydal_code = (
        '''db.define_table("users", Field("id", "id"), '''
        '''Field("name", "string"), Field("is_active", "boolean"))'''
    )

    result = convert_models(pydal_code, models_type="pydantic")

    module = load_generated_code(result)

    # Verify model class exists
    assert hasattr(module, "User")

    # Verify it's a Pydantic model by checking it has model_fields (Pydantic v2)
    # or __fields__ (Pydantic v1)
    assert hasattr(module.User, "model_fields") or hasattr(module.User, "__fields__")

    # Create an instance to verify the model works
    user = module.User(id=1, name="Test", is_active=True)
    assert user.id == 1
    assert user.name == "Test"
    assert user.is_active is True

    os.remove(os.path.abspath(module.__file__))


def test_pydal_to_dataclass_valid_model(load_generated_code) -> None:
    """Integration test: verify converted Pydal models are valid dataclasses."""
    pydal_code = (
        '''db.define_table("users", Field("id", "id"), '''
        '''Field("name", "string"), Field("score", "float"))'''
    )

    result = convert_models(pydal_code, models_type="dataclass")

    module = load_generated_code(result)

    # Verify model class exists
    assert hasattr(module, "User")

    # Verify it's a dataclass
    from dataclasses import is_dataclass
    assert is_dataclass(module.User)

    # Create an instance to verify the dataclass works
    user = module.User(id=1, name="Test", score=9.5)
    assert user.id == 1
    assert user.name == "Test"
    assert user.score == 9.5

    os.remove(os.path.abspath(module.__file__))
