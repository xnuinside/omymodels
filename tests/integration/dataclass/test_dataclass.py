"""Integration tests for Python dataclass generation."""

import os
from dataclasses import fields, is_dataclass

from omymodels import create_models


def test_dataclass_basic_model_is_valid(load_generated_code) -> None:
    """Integration test: verify generated dataclass models are valid."""
    ddl = """
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        name VARCHAR(100)
    );
    """
    result = create_models(ddl, models_type="dataclass")["code"]

    module = load_generated_code(result)

    # Verify dataclass exists
    assert hasattr(module, "Users")
    assert is_dataclass(module.Users)

    # Create instance
    user = module.Users(id=1, email="test@example.com", name="Test")
    assert user.id == 1
    assert user.email == "test@example.com"

    os.remove(os.path.abspath(module.__file__))


def test_dataclass_fields_are_correct(load_generated_code) -> None:
    """Integration test: verify dataclass fields are properly defined."""
    ddl = """
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        price DECIMAL(10,2),
        description TEXT
    );
    """
    result = create_models(ddl, models_type="dataclass")["code"]

    module = load_generated_code(result)

    assert is_dataclass(module.Products)

    # Check fields exist
    field_names = [f.name for f in fields(module.Products)]
    assert "id" in field_names
    assert "name" in field_names
    assert "price" in field_names
    assert "description" in field_names

    os.remove(os.path.abspath(module.__file__))


def test_dataclass_with_defaults(load_generated_code) -> None:
    """Integration test: verify dataclass handles default values."""
    ddl = """
    CREATE TABLE config (
        id SERIAL PRIMARY KEY,
        max_retries INTEGER DEFAULT 3,
        timeout INTEGER DEFAULT 30
    );
    """
    result = create_models(ddl, models_type="dataclass")["code"]

    module = load_generated_code(result)

    # Create instance - defaults should work
    config = module.Config(id=1)
    assert config.id == 1
    assert config.max_retries == 3

    os.remove(os.path.abspath(module.__file__))


def test_dataclass_multiple_tables(load_generated_code) -> None:
    """Integration test: verify multiple dataclasses are generated."""
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
    result = create_models(ddl, models_type="dataclass")["code"]

    module = load_generated_code(result)

    # Both should be dataclasses
    assert is_dataclass(module.Users)
    assert is_dataclass(module.Posts)

    # Create instances
    user = module.Users(id=1, name="Test")
    post = module.Posts(id=1, title="Hello", content="World")

    assert user.name == "Test"
    assert post.title == "Hello"

    os.remove(os.path.abspath(module.__file__))
