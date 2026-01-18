"""Tests for SQLAlchemy 2.0 ORM model generation."""

from omymodels import create_models


def test_basic_table():
    """Test basic table generation with SQLAlchemy 2.0 syntax."""
    ddl = """
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
"""
    result = create_models(ddl, models_type="sqlalchemy_v2")
    code = result["code"]

    # Check imports
    assert "from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column" in code
    assert "from datetime import datetime" in code
    assert "from sqlalchemy.sql import func" in code

    # Check Base class
    assert "class Base(DeclarativeBase):" in code

    # Check model definition
    assert "class Users(Base):" in code
    assert "__tablename__ = 'users'" in code

    # Check Mapped type hints with SQLAlchemy 2.0 style
    assert "id: Mapped[int] = mapped_column(" in code
    assert "email: Mapped[str] = mapped_column(String(255)" in code
    assert "name: Mapped[str | None] = mapped_column(String(100)" in code
    assert "is_active: Mapped[bool | None] = mapped_column(Boolean" in code
    assert "created_at: Mapped[datetime | None] = mapped_column(DateTime" in code

    # Check attributes
    assert "primary_key=True" in code
    assert "autoincrement=True" in code
    assert "server_default=func.now()" in code


def test_foreign_keys():
    """Test foreign key generation in SQLAlchemy 2.0 style."""
    ddl = """
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    total DECIMAL(10,2)
);

ALTER TABLE orders ADD FOREIGN KEY (user_id) REFERENCES users (id);
"""
    result = create_models(ddl, models_type="sqlalchemy_v2")
    code = result["code"]

    assert "from sqlalchemy import ForeignKey" in code
    assert "user_id: Mapped[int] = mapped_column(Integer" in code
    assert "ForeignKey('users.id')" in code


def test_multiple_types():
    """Test various column types in SQLAlchemy 2.0."""
    ddl = """
CREATE TABLE all_types (
    id INT PRIMARY KEY,
    col_text TEXT,
    col_date DATE,
    col_time TIME,
    col_float FLOAT,
    col_numeric DECIMAL(10,2),
    col_bigint BIGINT,
    col_smallint SMALLINT,
    col_binary BINARY
);
"""
    result = create_models(ddl, models_type="sqlalchemy_v2")
    code = result["code"]

    assert "col_text: Mapped[str | None] = mapped_column(Text" in code
    assert "col_date: Mapped[date | None] = mapped_column(Date" in code
    assert "col_time: Mapped[time | None] = mapped_column(Time" in code
    assert "col_float: Mapped[float | None] = mapped_column(Float" in code
    assert "col_numeric: Mapped[float | None] = mapped_column(Numeric(10,2)" in code
    assert "col_bigint: Mapped[int | None] = mapped_column(BigInteger" in code
    assert "col_smallint: Mapped[int | None] = mapped_column(SmallInteger" in code
    assert "col_binary: Mapped[bytes | None] = mapped_column(LargeBinary" in code

    # Check datetime imports
    assert "from datetime import" in code


def test_with_enums():
    """Test enum generation in SQLAlchemy 2.0 style."""
    ddl = """
CREATE TYPE status_type AS ENUM ('active', 'inactive', 'pending');

CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    status status_type
);
"""
    result = create_models(ddl, models_type="sqlalchemy_v2")
    code = result["code"]

    assert "class Items(Base):" in code
    assert "status: Mapped[" in code


def test_with_indexes():
    """Test index generation in SQLAlchemy 2.0 style."""
    ddl = """
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(50)
);

CREATE INDEX idx_products_name ON products (name);
CREATE UNIQUE INDEX idx_products_sku ON products (sku);
"""
    result = create_models(ddl, models_type="sqlalchemy_v2")
    code = result["code"]

    assert "__table_args__" in code
    assert "Index(" in code
    assert "UniqueConstraint(" in code


def test_with_schema():
    """Test schema support in SQLAlchemy 2.0 style."""
    ddl = """
CREATE TABLE "myschema"."users" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);
"""
    result = create_models(ddl, models_type="sqlalchemy_v2", schema_global=False)
    code = result["code"]

    assert "__table_args__" in code
    assert 'schema="myschema"' in code


def test_full_example():
    """Test a complete example matching the expected SQLAlchemy 2.0 output."""
    ddl = """
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
"""
    result = create_models(ddl, models_type="sqlalchemy_v2")
    code = result["code"]

    # Verify the generated code follows SQLAlchemy 2.0 conventions
    assert "DeclarativeBase" in code
    assert "Mapped[" in code
    assert "mapped_column(" in code
    assert "| None" in code  # Optional types use union syntax

    # Should NOT contain old-style SQLAlchemy patterns
    assert "sa.Column(" not in code
    assert "declarative_base()" not in code


def test_array_types():
    """Test PostgreSQL array types in SQLAlchemy 2.0."""
    ddl = """
CREATE TABLE array_test (
    id SERIAL PRIMARY KEY,
    tags TEXT[],
    scores INTEGER[]
);
"""
    result = create_models(ddl, models_type="sqlalchemy_v2")
    code = result["code"]

    assert "from typing import List" in code
    assert "from sqlalchemy.dialects.postgresql import ARRAY" in code
    assert "Mapped[List[str] | None]" in code
    assert "Mapped[List[int] | None]" in code
    assert "ARRAY(" in code


def test_relationships_with_back_populates():
    """Test that relationships=True generates relationship() with back_populates."""
    ddl = """
CREATE TABLE users (
  id int PRIMARY KEY,
  name varchar NOT NULL
);

CREATE TABLE posts (
  id int PRIMARY KEY,
  title varchar NOT NULL,
  user_id int
);

ALTER TABLE posts ADD FOREIGN KEY (user_id) REFERENCES users (id);
"""
    result = create_models(ddl, models_type="sqlalchemy_v2", relationships=True)
    code = result["code"]

    # Check relationship import
    assert "from sqlalchemy.orm import relationship" in code

    # Check parent (Users) has posts relationship
    assert 'posts: Mapped[List["Posts"]] = relationship("Posts", back_populates="user")' in code

    # Check child (Posts) has user relationship
    assert 'user: Mapped["Users"] = relationship("Users", back_populates="posts")' in code


def test_relationships_multiple_foreign_keys():
    """Test relationships with multiple foreign keys in the same table."""
    ddl = """
CREATE TABLE users (
  id int PRIMARY KEY,
  name varchar
);

CREATE TABLE posts (
  id int PRIMARY KEY,
  title varchar
);

CREATE TABLE comments (
  id int PRIMARY KEY,
  text varchar,
  user_id int,
  post_id int
);

ALTER TABLE comments ADD FOREIGN KEY (user_id) REFERENCES users (id);
ALTER TABLE comments ADD FOREIGN KEY (post_id) REFERENCES posts (id);
"""
    result = create_models(ddl, models_type="sqlalchemy_v2", relationships=True)
    code = result["code"]

    # Check parent relationships
    assert 'comments: Mapped[List["Comments"]] = relationship("Comments", back_populates="user")' in code
    assert 'comments: Mapped[List["Comments"]] = relationship("Comments", back_populates="post")' in code

    # Check child relationships
    assert 'user: Mapped["Users"] = relationship("Users", back_populates="comments")' in code
    assert 'post: Mapped["Posts"] = relationship("Posts", back_populates="comments")' in code
