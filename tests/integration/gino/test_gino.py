"""Integration tests for GinoORM generation.

NOTE: Gino requires SQLAlchemy<1.4, which conflicts with SQLAlchemy>=2.0
used for other tests. These tests are skipped in CI due to dependency conflicts.
To run these tests locally, install gino in a separate virtual environment.
"""

import os

import pytest

from omymodels import create_models

try:
    from gino import Gino
    HAS_GINO = True
except ImportError:
    HAS_GINO = False

pytestmark = pytest.mark.skipif(
    not HAS_GINO,
    reason="Gino is not installed (requires SQLAlchemy<1.4, conflicts with SQLAlchemy>=2.0)"
)


def test_gino_basic_model_is_valid(load_generated_code) -> None:
    """Integration test: verify generated Gino models are valid."""
    ddl = """
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        name VARCHAR(100),
        is_active BOOLEAN DEFAULT TRUE
    );
    """
    result = create_models(ddl, models_type="gino")["code"]

    module = load_generated_code(result)

    # Verify db (Gino instance) exists
    assert hasattr(module, "db")

    # Verify model class exists
    assert hasattr(module, "Users")

    # Check the model has correct __tablename__
    assert module.Users.__tablename__ == "users"

    os.remove(os.path.abspath(module.__file__))


def test_gino_model_columns(load_generated_code) -> None:
    """Integration test: verify Gino model columns are properly defined."""
    ddl = """
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        price DECIMAL(10,2),
        description TEXT
    );
    """
    result = create_models(ddl, models_type="gino")["code"]

    module = load_generated_code(result)

    # Verify model exists
    assert hasattr(module, "Products")
    assert module.Products.__tablename__ == "products"

    os.remove(os.path.abspath(module.__file__))


def test_gino_multiple_tables(load_generated_code) -> None:
    """Integration test: verify multiple Gino models generate correctly."""
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
    result = create_models(ddl, models_type="gino")["code"]

    module = load_generated_code(result)

    # Verify both models exist
    assert hasattr(module, "Users")
    assert hasattr(module, "Posts")

    # They should share the same db instance
    assert module.Users.__table__.metadata is module.Posts.__table__.metadata

    os.remove(os.path.abspath(module.__file__))


def test_gino_with_foreign_key(load_generated_code) -> None:
    """Integration test: verify foreign keys in Gino models."""
    ddl = """
    CREATE TABLE orders (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        total DECIMAL(10,2)
    );

    ALTER TABLE orders ADD FOREIGN KEY (user_id) REFERENCES users (id);
    """
    result = create_models(ddl, models_type="gino")["code"]

    module = load_generated_code(result)

    # Check model exists and has correct table
    assert hasattr(module, "Orders")
    assert module.Orders.__tablename__ == "orders"

    os.remove(os.path.abspath(module.__file__))
