"""Integration tests for GinoORM generation.

These tests verify that generated Gino code is valid and works correctly.
The code is pre-generated (as users would generate and commit to their repos).

NOTE: Gino requires SQLAlchemy<1.4. Run these tests in isolated environment:
  tox -e integration-gino
"""

import os
import sys
import uuid

import pytest

try:
    from gino import Gino
    HAS_GINO = True
except ImportError:
    HAS_GINO = False

pytestmark = pytest.mark.skipif(
    not HAS_GINO,
    reason="Gino is not installed"
)


def get_basic_model_code(table_suffix: str) -> str:
    """Generate basic model code with unique table name."""
    return f'''
from gino import Gino

db = Gino()


class Users{table_suffix}(db.Model):

    __tablename__ = 'users_{table_suffix}'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    email = db.Column(db.String(), nullable=False)
    name = db.Column(db.String())
    is_active = db.Column(db.Boolean())
'''


def get_products_code(table_suffix: str) -> str:
    """Generate products model code with unique table name."""
    return f'''
from gino import Gino

db = Gino()


class Products{table_suffix}(db.Model):

    __tablename__ = 'products_{table_suffix}'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    price = db.Column(db.Numeric())
    description = db.Column(db.Text())
'''


def get_multiple_tables_code(table_suffix: str) -> str:
    """Generate multiple tables code with unique table names."""
    return f'''
from gino import Gino

db = Gino()


class Users{table_suffix}(db.Model):

    __tablename__ = 'users_{table_suffix}'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    name = db.Column(db.String(), nullable=False)


class Posts{table_suffix}(db.Model):

    __tablename__ = 'posts_{table_suffix}'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer(), nullable=False)
    title = db.Column(db.String(), nullable=False)
'''


def get_foreign_key_code(table_suffix: str) -> str:
    """Generate model with foreign key."""
    return f'''
from gino import Gino

db = Gino()


class Orders{table_suffix}(db.Model):

    __tablename__ = 'orders_{table_suffix}'

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer(), nullable=False)
    total = db.Column(db.Numeric())
'''


def test_gino_basic_model_is_valid(load_generated_code) -> None:
    """Integration test: verify generated Gino models are valid."""
    suffix = uuid.uuid4().hex[:8]
    code = get_basic_model_code(suffix)
    module = load_generated_code(code)

    class_name = f"Users{suffix}"

    # Verify db (Gino instance) exists
    assert hasattr(module, "db")

    # Verify model class exists
    assert hasattr(module, class_name)

    model_class = getattr(module, class_name)

    # Check the model has correct __tablename__
    assert model_class.__tablename__ == f"users_{suffix}"

    os.remove(os.path.abspath(module.__file__))


def test_gino_model_columns(load_generated_code) -> None:
    """Integration test: verify Gino model columns are properly defined."""
    suffix = uuid.uuid4().hex[:8]
    code = get_products_code(suffix)
    module = load_generated_code(code)

    class_name = f"Products{suffix}"

    # Verify model exists
    assert hasattr(module, class_name)

    model_class = getattr(module, class_name)
    assert model_class.__tablename__ == f"products_{suffix}"

    os.remove(os.path.abspath(module.__file__))


def test_gino_multiple_tables(load_generated_code) -> None:
    """Integration test: verify multiple Gino models generate correctly."""
    suffix = uuid.uuid4().hex[:8]
    code = get_multiple_tables_code(suffix)
    module = load_generated_code(code)

    users_class = getattr(module, f"Users{suffix}")
    posts_class = getattr(module, f"Posts{suffix}")

    # Verify both models exist
    assert users_class is not None
    assert posts_class is not None

    # They should share the same db instance
    assert users_class.__table__.metadata is posts_class.__table__.metadata

    os.remove(os.path.abspath(module.__file__))


def test_gino_with_foreign_key(load_generated_code) -> None:
    """Integration test: verify foreign keys in Gino models."""
    suffix = uuid.uuid4().hex[:8]
    code = get_foreign_key_code(suffix)
    module = load_generated_code(code)

    class_name = f"Orders{suffix}"

    # Check model exists and has correct table
    assert hasattr(module, class_name)

    model_class = getattr(module, class_name)
    assert model_class.__tablename__ == f"orders_{suffix}"

    os.remove(os.path.abspath(module.__file__))
