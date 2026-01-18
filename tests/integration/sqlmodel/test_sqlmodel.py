"""Integration tests for SQLModel generation.

NOTE: SQLModel requires Pydantic>=2.0, which conflicts with table-meta
that requires Pydantic<2.0. These tests are skipped in CI due to dependency conflicts.
To run these tests locally, install sqlmodel in a separate virtual environment.
"""

import os
import sys

import pytest

from omymodels import create_models

try:
    from sqlmodel import SQLModel
    HAS_SQLMODEL = True
except ImportError:
    HAS_SQLMODEL = False

pytestmark = [
    pytest.mark.skipif(
        not HAS_SQLMODEL,
        reason="SQLModel is not installed (requires Pydantic>=2.0, conflicts with table-meta)"
    ),
    pytest.mark.skipif(
        sys.version_info < (3, 10),
        reason="SQLModel tests require Python 3.10+ for type syntax"
    ),
]


def test_sqlmodel_basic_model_is_valid(load_generated_code) -> None:
    """Integration test: verify generated SQLModel models are valid."""
    ddl = """
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        name VARCHAR(100),
        is_active BOOLEAN DEFAULT TRUE
    );
    """
    result = create_models(ddl, models_type="sqlmodel")["code"]

    module = load_generated_code(result)

    # Verify model class exists
    assert hasattr(module, "Users")

    # Check the model has correct __tablename__
    assert module.Users.__tablename__ == "users"

    # Check it's a SQLModel
    assert issubclass(module.Users, SQLModel)

    os.remove(os.path.abspath(module.__file__))


def test_sqlmodel_create_instance(load_generated_code) -> None:
    """Integration test: verify SQLModel instances can be created."""
    ddl = """
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        price DECIMAL(10,2)
    );
    """
    result = create_models(ddl, models_type="sqlmodel")["code"]

    module = load_generated_code(result)

    # Create instance
    product = module.Products(id=1, name="Test Product", price=99.99)
    assert product.id == 1
    assert product.name == "Test Product"
    assert product.price == 99.99

    os.remove(os.path.abspath(module.__file__))


def test_sqlmodel_with_nullable_fields(load_generated_code) -> None:
    """Integration test: verify nullable fields work correctly."""
    ddl = """
    CREATE TABLE config (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        max_retries INTEGER
    );
    """
    result = create_models(ddl, models_type="sqlmodel")["code"]

    module = load_generated_code(result)

    # Create instance with only required fields
    config = module.Config(id=1, name="Test")
    assert config.id == 1
    assert config.name == "Test"
    assert config.description is None

    os.remove(os.path.abspath(module.__file__))


def test_sqlmodel_multiple_tables(load_generated_code) -> None:
    """Integration test: verify multiple SQLModel tables generate correctly."""
    ddl = """
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL
    );

    CREATE TABLE posts (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        title VARCHAR(200) NOT NULL
    );
    """
    result = create_models(ddl, models_type="sqlmodel")["code"]

    module = load_generated_code(result)

    # Verify both models exist and are SQLModel subclasses
    assert hasattr(module, "Users")
    assert hasattr(module, "Posts")

    assert issubclass(module.Users, SQLModel)
    assert issubclass(module.Posts, SQLModel)

    os.remove(os.path.abspath(module.__file__))
