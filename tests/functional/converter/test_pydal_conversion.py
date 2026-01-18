"""Tests for Pydal model conversion to various output formats."""

from omymodels import convert_models


# === SQLAlchemy Tests ===


def test_basic_pydal_to_sqlalchemy():
    """Test basic Pydal table conversion to SQLAlchemy."""
    # Using "id" type which is Pydal's primary key type
    pydal_code = (
        '''db.define_table("users", Field("id", "id"), '''
        '''Field("name", "string"), Field("email", "string"))'''
    )

    result = convert_models(pydal_code, models_type="sqlalchemy")

    assert "class User(Base):" in result
    assert "__tablename__ = 'users'" in result
    assert "id = sa.Column(sa.Integer(), primary_key=True)" in result
    assert "name = sa.Column(sa.String())" in result
    assert "email = sa.Column(sa.String())" in result


def test_pydal_to_sqlalchemy_v2():
    """Test Pydal table conversion to SQLAlchemy 2.0 style."""
    pydal_code = '''db.define_table("users", Field("id", "id"), Field("name", "string"))'''

    result = convert_models(pydal_code, models_type="sqlalchemy_v2")

    assert "class User(Base):" in result
    assert "__tablename__ = 'users'" in result
    assert "primary_key=True" in result
    assert "name: Mapped[str | None] = mapped_column(String)" in result


def test_pydal_multiple_tables():
    """Test conversion of multiple Pydal tables."""
    pydal_code = '''db.define_table("users", Field("id", "id"), Field("name", "string"))

db.define_table("posts", Field("id", "id"), Field("title", "string"))'''

    result = convert_models(pydal_code, models_type="sqlalchemy")

    assert "class User(Base):" in result
    assert "class Post(Base):" in result
    assert "__tablename__ = 'users'" in result
    assert "__tablename__ = 'posts'" in result


def test_pydal_foreign_key():
    """Test Pydal reference type conversion to SQLAlchemy ForeignKey."""
    pydal_code = '''db.define_table("users", Field("id", "id"), Field("name", "string"))

db.define_table("posts", Field("id", "id"), Field("title", "string"), \
Field("user_id", "reference users"))'''

    result = convert_models(pydal_code, models_type="sqlalchemy")

    assert "class User(Base):" in result
    assert "class Post(Base):" in result
    assert "user_id = sa.Column(sa.Integer(), sa.ForeignKey('users.id'))" in result


def test_pydal_foreign_key_v2():
    """Test Pydal reference type conversion to SQLAlchemy v2 ForeignKey."""
    pydal_code = '''db.define_table("users", Field("id", "id"), Field("name", "string"))

db.define_table("posts", Field("id", "id"), Field("user_id", "reference users"))'''

    result = convert_models(pydal_code, models_type="sqlalchemy_v2")

    assert "from sqlalchemy import ForeignKey" in result
    assert "user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id'))" in result


def test_pydal_various_types():
    """Test conversion of various Pydal types."""
    pydal_code = '''db.define_table("test_types", Field("id", "id"),
                Field("col_string", "string"),
                Field("col_text", "text"),
                Field("col_integer", "integer"),
                Field("col_boolean", "boolean"),
                Field("col_datetime", "datetime"),
                Field("col_date", "date"),
                Field("col_float", "float"),
                Field("col_decimal", "decimal"))'''

    result = convert_models(pydal_code, models_type="sqlalchemy")

    assert "col_string = sa.Column(sa.String())" in result
    assert "col_text = sa.Column(sa.Text())" in result
    assert "col_integer = sa.Column(sa.Integer())" in result
    assert "col_boolean = sa.Column(sa.Boolean())" in result
    assert "col_datetime = sa.Column(sa.DateTime())" in result
    assert "col_date = sa.Column(sa.Date())" in result
    assert "col_float = sa.Column(sa.Float())" in result
    assert "col_decimal = sa.Column(sa.Numeric())" in result


def test_pydal_table_name_preserved():
    """Test that Pydal table names are preserved without pluralization."""
    pydal_code = '''db.define_table("my_table", Field("id", "id"))'''

    result = convert_models(pydal_code, models_type="sqlalchemy")

    # Table name should be preserved as 'my_table', not pluralized
    assert "__tablename__ = 'my_table'" in result
    # Class name should be derived from table name
    assert "class MyTable(Base):" in result


def test_pydal_id_type_is_primary_key():
    """Test that Pydal 'id' type creates a primary key."""
    pydal_code = '''db.define_table("users", Field("id", "id"), Field("name", "string"))'''

    result = convert_models(pydal_code, models_type="sqlalchemy")

    assert "primary_key=True" in result


# === Gino Tests ===


def test_pydal_to_gino():
    """Test Pydal table conversion to Gino ORM."""
    pydal_code = (
        '''db.define_table("users", Field("id", "id"), '''
        '''Field("name", "string"), Field("email", "string"))'''
    )

    result = convert_models(pydal_code, models_type="gino")

    assert "from gino import Gino" in result
    assert "db = Gino()" in result
    assert "class User(db.Model):" in result
    assert "__tablename__ = 'users'" in result
    assert "id = db.Column(db.Integer(), primary_key=True)" in result
    assert "name = db.Column(db.String())" in result
    assert "email = db.Column(db.String())" in result


def test_pydal_to_gino_with_foreign_key():
    """Test Pydal reference type conversion to Gino ForeignKey."""
    pydal_code = '''db.define_table("users", Field("id", "id"), Field("name", "string"))

db.define_table("posts", Field("id", "id"), Field("user_id", "reference users"))'''

    result = convert_models(pydal_code, models_type="gino")

    assert "class User(db.Model):" in result
    assert "class Post(db.Model):" in result
    assert "user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))" in result


# === Pydantic Tests ===


def test_pydal_to_pydantic():
    """Test Pydal table conversion to Pydantic."""
    pydal_code = (
        '''db.define_table("users", Field("id", "id"), '''
        '''Field("name", "string"), Field("is_active", "boolean"))'''
    )

    result = convert_models(pydal_code, models_type="pydantic")

    assert "from pydantic import BaseModel" in result
    assert "class User(BaseModel):" in result
    assert "id: Optional[int]" in result
    assert "name: Optional[str]" in result
    assert "is_active: Optional[bool]" in result


def test_pydal_to_pydantic_v2():
    """Test Pydal table conversion to Pydantic v2."""
    pydal_code = (
        '''db.define_table("users", Field("id", "id"), '''
        '''Field("name", "string"), Field("is_active", "boolean"))'''
    )

    result = convert_models(pydal_code, models_type="pydantic_v2")

    assert "from pydantic import BaseModel" in result
    assert "class User(BaseModel):" in result
    assert "id: int | None" in result
    assert "name: str | None" in result
    assert "is_active: bool | None" in result


# === Dataclass Tests ===


def test_pydal_to_dataclass():
    """Test Pydal table conversion to Python dataclass."""
    pydal_code = (
        '''db.define_table("users", Field("id", "id"), '''
        '''Field("name", "string"), Field("score", "float"))'''
    )

    result = convert_models(pydal_code, models_type="dataclass")

    assert "from dataclasses import dataclass" in result
    assert "@dataclass" in result
    assert "class User:" in result
    assert "id: int" in result
    assert "name: str" in result
    assert "score: float" in result


# === SQLModel Tests ===


def test_pydal_to_sqlmodel():
    """Test Pydal table conversion to SQLModel."""
    pydal_code = (
        '''db.define_table("users", Field("id", "id"), '''
        '''Field("name", "string"), Field("email", "string"))'''
    )

    result = convert_models(pydal_code, models_type="sqlmodel")

    assert "from sqlmodel import" in result
    assert "SQLModel" in result
    assert "class User(SQLModel, table=True):" in result
    assert "__tablename__ = 'users'" in result
    assert "id: int | None" in result or "id: Optional[int]" in result
    assert "name: str | None" in result or "name: Optional[str]" in result


def test_pydal_to_sqlmodel_with_foreign_key():
    """Test Pydal reference type conversion to SQLModel ForeignKey."""
    pydal_code = '''db.define_table("users", Field("id", "id"), Field("name", "string"))

db.define_table("posts", Field("id", "id"), Field("user_id", "reference users"))'''

    result = convert_models(pydal_code, models_type="sqlmodel")

    assert "class User(SQLModel, table=True):" in result
    assert "class Post(SQLModel, table=True):" in result
    assert "foreign_key='users.id'" in result
