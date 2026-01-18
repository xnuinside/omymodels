"""Integration tests for OpenAPI 3 schema generation and conversion."""

import json
import os
import sys
import importlib
import uuid

import pytest

from omymodels import create_models, create_models_from_openapi3


def test_openapi3_generates_valid_json() -> None:
    """Integration test: verify generated OpenAPI schema is valid JSON."""
    ddl = """
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(255),
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP
    );
    """
    result = create_models(ddl, models_type="openapi3")["code"]

    # Should be valid JSON
    schema = json.loads(result)

    # Should have components.schemas structure
    assert "components" in schema
    assert "schemas" in schema["components"]
    assert "Users" in schema["components"]["schemas"]


def test_openapi3_correct_type_mappings() -> None:
    """Integration test: verify SQL types map to correct OpenAPI types."""
    ddl = """
    CREATE TABLE all_types (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        price DECIMAL(10,2),
        is_active BOOLEAN,
        created_at TIMESTAMP,
        event_date DATE,
        event_time TIME,
        user_id UUID,
        metadata JSON,
        data JSONB,
        file_content BYTEA
    );
    """
    result = create_models(ddl, models_type="openapi3")["code"]
    schema = json.loads(result)

    props = schema["components"]["schemas"]["AllTypes"]["properties"]

    # Integer
    assert props["id"]["type"] == "integer"

    # String with maxLength
    assert props["name"]["type"] == "string"
    assert props["name"]["maxLength"] == 100

    # Text (string without maxLength)
    assert props["description"]["type"] == "string"

    # Decimal/Number
    assert props["price"]["type"] == "number"

    # Boolean
    assert props["is_active"]["type"] == "boolean"

    # Timestamp
    assert props["created_at"]["type"] == "string"
    assert props["created_at"]["format"] == "date-time"

    # Date
    assert props["event_date"]["type"] == "string"
    assert props["event_date"]["format"] == "date"

    # Time
    assert props["event_time"]["type"] == "string"
    assert props["event_time"]["format"] == "time"

    # UUID
    assert props["user_id"]["type"] == "string"
    assert props["user_id"]["format"] == "uuid"

    # JSON/JSONB
    assert props["metadata"]["type"] == "object"
    assert props["data"]["type"] == "object"

    # Binary (bytea maps to byte format)
    assert props["file_content"]["type"] == "string"
    assert props["file_content"]["format"] == "byte"


def test_openapi3_required_fields() -> None:
    """Integration test: verify required fields are properly marked."""
    ddl = """
    CREATE TABLE products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        price DECIMAL(10,2) NOT NULL,
        category VARCHAR(50) DEFAULT 'general'
    );
    """
    result = create_models(ddl, models_type="openapi3")["code"]
    schema = json.loads(result)

    products_schema = schema["components"]["schemas"]["Products"]

    # Fields without default and NOT NULL should be required
    assert "required" in products_schema
    required = products_schema["required"]

    # id, name, price should be required (NOT NULL and no default)
    assert "id" in required
    assert "name" in required
    assert "price" in required

    # description (nullable) and category (has default) should NOT be required
    assert "description" not in required
    assert "category" not in required


def test_openapi3_array_types() -> None:
    """Integration test: verify array types are properly generated."""
    ddl = """
    CREATE TABLE array_test (
        id SERIAL PRIMARY KEY,
        tags TEXT[],
        scores INTEGER[]
    );
    """
    result = create_models(ddl, models_type="openapi3")["code"]
    schema = json.loads(result)

    props = schema["components"]["schemas"]["ArrayTest"]["properties"]

    # Arrays should have type: array and items
    assert props["tags"]["type"] == "array"
    assert props["tags"]["items"]["type"] == "string"

    assert props["scores"]["type"] == "array"
    assert props["scores"]["items"]["type"] == "integer"


def test_openapi3_multiple_tables() -> None:
    """Integration test: verify multiple tables generate separate schemas."""
    ddl = """
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL
    );

    CREATE TABLE posts (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        title VARCHAR(200) NOT NULL,
        content TEXT
    );

    CREATE TABLE comments (
        id SERIAL PRIMARY KEY,
        post_id INTEGER NOT NULL,
        author VARCHAR(100),
        body TEXT
    );
    """
    result = create_models(ddl, models_type="openapi3")["code"]
    schema = json.loads(result)

    schemas = schema["components"]["schemas"]

    # All three tables should be present
    assert "Users" in schemas
    assert "Posts" in schemas
    assert "Comments" in schemas


def test_openapi3_default_values() -> None:
    """Integration test: verify default values are properly set."""
    ddl = """
    CREATE TABLE config (
        id SERIAL PRIMARY KEY,
        max_retries INTEGER DEFAULT 3,
        timeout DECIMAL(5,2) DEFAULT 30.5,
        is_enabled BOOLEAN DEFAULT TRUE
    );
    """
    result = create_models(ddl, models_type="openapi3")["code"]
    schema = json.loads(result)

    props = schema["components"]["schemas"]["Config"]["properties"]

    # Integer default
    assert props["max_retries"]["default"] == 3

    # Float default
    assert props["timeout"]["default"] == 30.5

    # Boolean default
    assert props["is_enabled"]["default"] is True


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="pydantic_v2 syntax requires Python 3.10+ for runtime evaluation"
)
def test_openapi3_to_pydantic_conversion() -> None:
    """Integration test: verify OpenAPI to Pydantic conversion works."""
    openapi_schema = """
    {
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                        "is_active": {"type": "boolean"}
                    },
                    "required": ["id", "name"]
                }
            }
        }
    }
    """

    result = create_models_from_openapi3(openapi_schema, models_type="pydantic_v2")

    # Should contain Pydantic model definition
    assert "class User(BaseModel):" in result
    assert "id: int" in result
    assert "name: str" in result
    # Optional fields should have | None
    assert "email: str | None" in result
    assert "is_active: bool | None" in result


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="pydantic_v2 syntax requires Python 3.10+ for runtime evaluation"
)
def test_openapi3_to_pydantic_roundtrip() -> None:
    """Integration test: verify DDL -> OpenAPI -> Pydantic works correctly."""
    # Step 1: Create OpenAPI schema from DDL
    ddl = """
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(255),
        is_verified BOOLEAN DEFAULT FALSE
    );
    """
    openapi_result = create_models(ddl, models_type="openapi3")["code"]

    # Verify it's valid JSON
    json.loads(openapi_result)

    # Step 2: Convert OpenAPI to Pydantic
    pydantic_result = create_models_from_openapi3(openapi_result, models_type="pydantic_v2")

    # Should contain Pydantic model
    assert "class Users(BaseModel):" in pydantic_result
    assert "username: str" in pydantic_result
