import os
import sys

import pytest

from omymodels import create_models

try:
    import sqlalchemy
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False

# SQLAlchemy 2.0 style with X | None syntax requires Python 3.10+
pytestmark = [
    pytest.mark.skipif(
        sys.version_info < (3, 10),
        reason="sqlalchemy_v2 syntax requires Python 3.10+ for runtime evaluation"
    ),
    pytest.mark.skipif(
        not HAS_SQLALCHEMY,
        reason="SQLAlchemy is not installed"
    ),
]


def test_sqlalchemy_v2_basic_model_is_valid(load_generated_code) -> None:
    """Integration test: verify generated SQLAlchemy 2.0 models are valid."""
    ddl = """
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        name VARCHAR(100),
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """
    result = create_models(ddl, models_type="sqlalchemy_v2")["code"]

    module = load_generated_code(result)

    # Verify Base class exists
    assert hasattr(module, "Base")

    # Verify model class exists
    assert hasattr(module, "Users")

    # Check the model has correct __tablename__
    assert module.Users.__tablename__ == "users"

    # Check model inherits from Base
    assert issubclass(module.Users, module.Base)

    os.remove(os.path.abspath(module.__file__))


def test_sqlalchemy_v2_model_columns_are_mapped(load_generated_code) -> None:
    """Integration test: verify columns are properly mapped with Mapped type."""
    ddl = """
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        price DECIMAL(10,2),
        description TEXT
    );
    """
    result = create_models(ddl, models_type="sqlalchemy_v2")["code"]

    module = load_generated_code(result)

    # Verify columns exist in __table__.columns
    assert hasattr(module.Products, "__table__")
    column_names = [c.name for c in module.Products.__table__.columns]
    assert "id" in column_names
    assert "name" in column_names
    assert "price" in column_names
    assert "description" in column_names

    os.remove(os.path.abspath(module.__file__))


def test_sqlalchemy_v2_foreign_key_works(load_generated_code) -> None:
    """Integration test: verify foreign keys are properly defined."""
    ddl = """
    CREATE TABLE orders (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        total DECIMAL(10,2)
    );

    ALTER TABLE orders ADD FOREIGN KEY (user_id) REFERENCES users (id);
    """
    result = create_models(ddl, models_type="sqlalchemy_v2")["code"]

    module = load_generated_code(result)

    # Check foreign key exists
    user_id_col = module.Orders.__table__.columns["user_id"]
    assert len(user_id_col.foreign_keys) == 1

    os.remove(os.path.abspath(module.__file__))


def test_sqlalchemy_v2_array_types_work(load_generated_code) -> None:
    """Integration test: verify PostgreSQL array types are properly handled."""
    ddl = """
    CREATE TABLE array_test (
        id SERIAL PRIMARY KEY,
        tags TEXT[],
        scores INTEGER[]
    );
    """
    result = create_models(ddl, models_type="sqlalchemy_v2")["code"]

    module = load_generated_code(result)

    # Verify model exists and has correct columns
    assert hasattr(module, "ArrayTest")
    column_names = [c.name for c in module.ArrayTest.__table__.columns]
    assert "tags" in column_names
    assert "scores" in column_names

    os.remove(os.path.abspath(module.__file__))


def test_sqlalchemy_v2_datetime_types_work(load_generated_code) -> None:
    """Integration test: verify datetime types are properly handled."""
    ddl = """
    CREATE TABLE events (
        id SERIAL PRIMARY KEY,
        event_date DATE,
        event_time TIME,
        event_datetime TIMESTAMP
    );
    """
    result = create_models(ddl, models_type="sqlalchemy_v2")["code"]

    module = load_generated_code(result)

    # Verify model exists
    assert hasattr(module, "Events")

    # Check columns exist
    column_names = [c.name for c in module.Events.__table__.columns]
    assert "event_date" in column_names
    assert "event_time" in column_names
    assert "event_datetime" in column_names

    os.remove(os.path.abspath(module.__file__))


def test_sqlalchemy_v2_with_indexes(load_generated_code) -> None:
    """Integration test: verify indexes are properly generated."""
    ddl = """
    CREATE TABLE products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        sku VARCHAR(50)
    );

    CREATE INDEX idx_products_name ON products (name);
    CREATE UNIQUE INDEX idx_products_sku ON products (sku);
    """
    result = create_models(ddl, models_type="sqlalchemy_v2")["code"]

    module = load_generated_code(result)

    # Verify model exists and __table_args__ is defined
    assert hasattr(module, "Products")
    assert hasattr(module.Products, "__table_args__")

    os.remove(os.path.abspath(module.__file__))


def test_sqlalchemy_v2_complete_example(load_generated_code) -> None:
    """Integration test: verify a complete schema with multiple tables works."""
    ddl = """
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(255) NOT NULL,
        is_verified BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT NOW()
    );

    CREATE TABLE posts (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        title VARCHAR(200) NOT NULL,
        content TEXT,
        published_at TIMESTAMP
    );

    ALTER TABLE posts ADD FOREIGN KEY (user_id) REFERENCES users (id);
    """
    result = create_models(ddl, models_type="sqlalchemy_v2")["code"]

    module = load_generated_code(result)

    # Verify both models exist
    assert hasattr(module, "Users")
    assert hasattr(module, "Posts")

    # Verify they inherit from the same Base
    assert issubclass(module.Users, module.Base)
    assert issubclass(module.Posts, module.Base)

    # Verify foreign key on Posts
    user_id_col = module.Posts.__table__.columns["user_id"]
    assert len(user_id_col.foreign_keys) == 1

    os.remove(os.path.abspath(module.__file__))


def test_sqlalchemy_v2_relationships_with_back_populates(load_generated_code) -> None:
    """Integration test: verify relationship() with back_populates is generated correctly."""
    ddl = """
    CREATE TABLE authors (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL
    );

    CREATE TABLE books (
        id SERIAL PRIMARY KEY,
        title VARCHAR(200) NOT NULL,
        author_id INT
    );

    ALTER TABLE books ADD FOREIGN KEY (author_id) REFERENCES authors (id);
    """
    result = create_models(ddl, models_type="sqlalchemy_v2", relationships=True)["code"]

    module = load_generated_code(result)

    # Verify models exist
    assert hasattr(module, "Authors")
    assert hasattr(module, "Books")

    # Verify relationships are defined
    from sqlalchemy.orm import configure_mappers
    configure_mappers()

    # Check Authors has 'books' relationship
    author_relationships = module.Authors.__mapper__.relationships
    assert "books" in author_relationships.keys()

    # Check Books has 'author' relationship
    book_relationships = module.Books.__mapper__.relationships
    assert "author" in book_relationships.keys()

    os.remove(os.path.abspath(module.__file__))
