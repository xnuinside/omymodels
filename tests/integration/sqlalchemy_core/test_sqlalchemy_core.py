"""Integration tests for SQLAlchemy Core (Table) generation."""

import os

import pytest

from omymodels import create_models

try:
    from sqlalchemy import Table
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False

pytestmark = pytest.mark.skipif(
    not HAS_SQLALCHEMY,
    reason="SQLAlchemy is not installed"
)


def test_sqlalchemy_core_basic_table_is_valid(load_generated_code) -> None:
    """Integration test: verify generated SQLAlchemy Core tables are valid."""
    ddl = """
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        name VARCHAR(100),
        is_active BOOLEAN DEFAULT TRUE
    );
    """
    result = create_models(ddl, models_type="sqlalchemy_core")["code"]

    module = load_generated_code(result)

    # Verify metadata exists
    assert hasattr(module, "metadata")

    # Verify table exists
    assert hasattr(module, "users")
    assert isinstance(module.users, Table)

    os.remove(os.path.abspath(module.__file__))


def test_sqlalchemy_core_table_columns(load_generated_code) -> None:
    """Integration test: verify table columns are properly defined."""
    ddl = """
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        price DECIMAL(10,2),
        description TEXT
    );
    """
    result = create_models(ddl, models_type="sqlalchemy_core")["code"]

    module = load_generated_code(result)

    assert isinstance(module.products, Table)

    # Check columns exist
    column_names = [c.name for c in module.products.columns]
    assert "id" in column_names
    assert "name" in column_names
    assert "price" in column_names
    assert "description" in column_names

    os.remove(os.path.abspath(module.__file__))


def test_sqlalchemy_core_foreign_key(load_generated_code) -> None:
    """Integration test: verify foreign keys in Core tables."""
    ddl = """
    CREATE TABLE orders (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        total DECIMAL(10,2)
    );

    ALTER TABLE orders ADD FOREIGN KEY (user_id) REFERENCES users (id);
    """
    result = create_models(ddl, models_type="sqlalchemy_core")["code"]

    module = load_generated_code(result)

    # Check foreign key exists
    user_id_col = module.orders.columns["user_id"]
    assert len(user_id_col.foreign_keys) == 1

    os.remove(os.path.abspath(module.__file__))


def test_sqlalchemy_core_multiple_tables(load_generated_code) -> None:
    """Integration test: verify multiple Core tables generate correctly."""
    ddl = """
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL
    );

    CREATE TABLE posts (
        id SERIAL PRIMARY KEY,
        title VARCHAR(200) NOT NULL,
        content TEXT
    );
    """
    result = create_models(ddl, models_type="sqlalchemy_core")["code"]

    module = load_generated_code(result)

    # Verify both tables exist
    assert hasattr(module, "users")
    assert hasattr(module, "posts")

    assert isinstance(module.users, Table)
    assert isinstance(module.posts, Table)

    os.remove(os.path.abspath(module.__file__))


def test_sqlalchemy_core_with_index(load_generated_code) -> None:
    """Integration test: verify indexes are properly generated."""
    ddl = """
    CREATE TABLE products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        sku VARCHAR(50)
    );

    CREATE INDEX idx_products_name ON products (name);
    """
    result = create_models(ddl, models_type="sqlalchemy_core")["code"]

    module = load_generated_code(result)

    # Table should exist and be valid
    assert isinstance(module.products, Table)

    os.remove(os.path.abspath(module.__file__))
