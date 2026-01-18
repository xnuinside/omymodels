"""Tests for OpenAPI 3 schema generation and parsing."""

import json

import pytest

from omymodels import create_models, create_models_from_openapi3


class TestGenerateOpenAPI3:
    """Tests for generating OpenAPI 3 schemas from DDL."""

    def test_basic_table_to_openapi3(self):
        """Test generating OAS3 schema from basic table."""
        ddl = """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            email VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE
        );
        """

        result = create_models(ddl, models_type="openapi3")
        schema = json.loads(result["code"])

        assert "components" in schema
        assert "schemas" in schema["components"]
        assert "Users" in schema["components"]["schemas"]

        user_schema = schema["components"]["schemas"]["Users"]
        assert user_schema["type"] == "object"
        assert "id" in user_schema["properties"]
        assert "username" in user_schema["properties"]
        assert "email" in user_schema["properties"]
        assert "is_active" in user_schema["properties"]

        # Check required fields
        assert "id" in user_schema["required"]
        assert "username" in user_schema["required"]

    def test_openapi3_type_mapping(self):
        """Test that SQL types are correctly mapped to OAS3 types."""
        ddl = """
        CREATE TABLE test_types (
            id INTEGER PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            description TEXT,
            price DECIMAL(10,2),
            is_available BOOLEAN,
            created_at TIMESTAMP,
            birth_date DATE,
            user_id UUID,
            metadata JSONB
        );
        """

        result = create_models(ddl, models_type="openapi3")
        schema = json.loads(result["code"])
        props = schema["components"]["schemas"]["TestTypes"]["properties"]

        assert props["id"]["type"] == "integer"
        assert props["name"]["type"] == "string"
        assert props["name"]["maxLength"] == 50
        assert props["description"]["type"] == "string"
        assert props["price"]["type"] == "number"
        assert props["is_available"]["type"] == "boolean"
        assert props["created_at"]["type"] == "string"
        assert props["created_at"]["format"] == "date-time"
        assert props["birth_date"]["type"] == "string"
        assert props["birth_date"]["format"] == "date"
        assert props["user_id"]["type"] == "string"
        assert props["user_id"]["format"] == "uuid"
        assert props["metadata"]["type"] == "object"

    def test_multiple_tables_to_openapi3(self):
        """Test generating OAS3 schema from multiple tables."""
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
        """

        result = create_models(ddl, models_type="openapi3")
        schema = json.loads(result["code"])

        assert "Users" in schema["components"]["schemas"]
        assert "Posts" in schema["components"]["schemas"]


class TestParseOpenAPI3:
    """Tests for parsing OpenAPI 3 schemas and converting to Python models."""

    def test_basic_schema_to_pydantic(self):
        """Test converting OAS3 schema to Pydantic models."""
        schema = """
        {
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "email": {"type": "string"}
                        },
                        "required": ["id", "name"]
                    }
                }
            }
        }
        """

        result = create_models_from_openapi3(schema, models_type="pydantic")

        assert "from pydantic import BaseModel" in result
        assert "class User(BaseModel):" in result
        assert "id:" in result
        assert "name:" in result
        assert "email:" in result

    def test_schema_to_pydantic_v2(self):
        """Test converting OAS3 schema to Pydantic v2 models."""
        schema = """
        {
            "components": {
                "schemas": {
                    "Product": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "price": {"type": "number"},
                            "in_stock": {"type": "boolean", "default": true}
                        },
                        "required": ["id", "name"]
                    }
                }
            }
        }
        """

        result = create_models_from_openapi3(schema, models_type="pydantic_v2")

        assert "from pydantic import BaseModel" in result
        assert "class Product(BaseModel):" in result
        assert "id: int" in result
        assert "name: str" in result
        # Optional fields use union syntax
        assert "price:" in result
        assert "in_stock:" in result

    def test_schema_to_dataclass(self):
        """Test converting OAS3 schema to Python dataclasses."""
        schema = """
        {
            "components": {
                "schemas": {
                    "Order": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "customer_name": {"type": "string"},
                            "total": {"type": "number"}
                        },
                        "required": ["id"]
                    }
                }
            }
        }
        """

        result = create_models_from_openapi3(schema, models_type="dataclass")

        assert "from dataclasses import dataclass" in result
        assert "@dataclass" in result
        assert "class Order:" in result
        assert "id: int" in result
        assert "customer_name:" in result
        assert "total:" in result

    def test_schema_to_sqlalchemy(self):
        """Test converting OAS3 schema to SQLAlchemy models."""
        schema = """
        {
            "components": {
                "schemas": {
                    "Article": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "title": {"type": "string", "maxLength": 200},
                            "content": {"type": "string"},
                            "published": {"type": "boolean"}
                        },
                        "required": ["id", "title"]
                    }
                }
            }
        }
        """

        result = create_models_from_openapi3(schema, models_type="sqlalchemy")

        assert "import sqlalchemy as sa" in result
        assert "class Article(Base):" in result
        assert "id = sa.Column" in result
        assert "title = sa.Column" in result

    def test_datetime_format_handling(self):
        """Test that datetime formats are correctly converted."""
        schema = """
        {
            "components": {
                "schemas": {
                    "Event": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "event_date": {"type": "string", "format": "date"},
                            "start_time": {"type": "string", "format": "time"},
                            "created_at": {"type": "string", "format": "date-time"}
                        },
                        "required": ["id"]
                    }
                }
            }
        }
        """

        result = create_models_from_openapi3(schema, models_type="pydantic_v2")

        assert "import datetime" in result
        assert "class Event(BaseModel):" in result

    def test_empty_schema_raises_error(self):
        """Test that empty schema raises ValueError."""
        schema = '{"components": {"schemas": {}}}'

        with pytest.raises(ValueError, match="No schemas found"):
            create_models_from_openapi3(schema)

    def test_invalid_json_with_yaml(self):
        """Test YAML parsing fallback."""
        # This is valid YAML but not JSON
        yaml_schema = """
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
      required:
        - id
"""
        try:
            result = create_models_from_openapi3(yaml_schema, models_type="pydantic")
            assert "class User(BaseModel):" in result
        except ValueError as e:
            # If pyyaml not installed, should get appropriate error
            assert "pyyaml" in str(e).lower()


class TestRoundTrip:
    """Tests for round-trip conversion (DDL -> OAS3 -> Python models)."""

    def test_ddl_to_openapi3_to_pydantic(self):
        """Test converting DDL to OAS3 and back to Pydantic."""
        ddl = """
        CREATE TABLE products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            price DECIMAL(10,2),
            active BOOLEAN DEFAULT TRUE
        );
        """

        # DDL -> OpenAPI 3
        oas_result = create_models(ddl, models_type="openapi3")
        oas_schema = oas_result["code"]

        # OpenAPI 3 -> Pydantic
        pydantic_result = create_models_from_openapi3(
            oas_schema, models_type="pydantic_v2"
        )

        assert "class Products(BaseModel):" in pydantic_result
        assert "id: int" in pydantic_result
        assert "name: str" in pydantic_result
