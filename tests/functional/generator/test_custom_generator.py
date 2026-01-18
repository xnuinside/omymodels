"""Functional tests for custom generator registration and usage."""

import pytest

from omymodels import (
    BaseGenerator,
    TypeConverter,
    create_models,
    list_generators,
    register_generator,
    unregister_generator,
)
from omymodels.plugins import _custom_generators


class SimpleTestGenerator(BaseGenerator):
    """Simple test generator for testing the plugin system."""

    TYPE_MAPPING = {
        "varchar": "String",
        "integer": "Integer",
        "boolean": "Boolean",
        "timestamp": "DateTime",
        "serial": "AutoField",
    }

    def __init__(self):
        super().__init__()
        self.type_converter = TypeConverter(self.TYPE_MAPPING)

    def generate_model(self, table, singular=True, exceptions=None, **kwargs):
        class_name = table.name.title().replace("_", "")
        lines = [f"class {class_name}(TestModel):"]

        for column in table.columns:
            col_type = self.type_converter.convert(column.type)
            lines.append(f"    {column.name} = {col_type}()")

        return "\n".join(lines)

    def create_header(self, tables, **kwargs):
        return "from test_framework import TestModel\n"


@pytest.fixture(autouse=True)
def cleanup_custom_generators():
    """Clean up test generators before and after each test."""
    # Store state and clean test generators
    original = dict(_custom_generators)

    # Remove any test generators from previous runs
    to_remove = [k for k in _custom_generators if k.startswith("test_")]
    for k in to_remove:
        del _custom_generators[k]

    yield

    # Restore original state and remove any test generators
    to_remove = [k for k in _custom_generators if k.startswith("test_")]
    for k in to_remove:
        del _custom_generators[k]
    _custom_generators.update(original)


class TestCustomGeneratorIntegration:
    """Integration tests for using custom generators with create_models."""

    def test_register_and_use_custom_generator(self):
        """Test registering a custom generator and using it with create_models."""
        register_generator("test_simple", SimpleTestGenerator)

        ddl = """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE
        );
        """

        result = create_models(ddl, models_type="test_simple")
        code = result["code"]

        assert "from test_framework import TestModel" in code
        assert "class Users(TestModel):" in code
        assert "id = AutoField()" in code
        assert "name = String()" in code
        assert "is_active = Boolean()" in code

    def test_custom_generator_appears_in_list(self):
        """Test that registered generator appears in list_generators."""
        register_generator("test_listed", SimpleTestGenerator)

        generators = list_generators()

        assert "test_listed" in generators
        assert generators["test_listed"] == "custom"

    def test_unregister_removes_generator(self):
        """Test that unregister_generator removes the generator."""
        register_generator("test_remove", SimpleTestGenerator)
        assert "test_remove" in list_generators()

        result = unregister_generator("test_remove")

        assert result is True
        assert "test_remove" not in list_generators()

    def test_custom_generator_with_multiple_tables(self):
        """Test custom generator with multiple tables."""
        register_generator("test_multi", SimpleTestGenerator)

        ddl = """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100)
        );

        CREATE TABLE posts (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200),
            user_id INTEGER NOT NULL
        );
        """

        result = create_models(ddl, models_type="test_multi")
        code = result["code"]

        assert "class Users(TestModel):" in code
        assert "class Posts(TestModel):" in code

    def test_builtin_generators_still_work(self):
        """Test that built-in generators still work after registering custom one."""
        register_generator("test_custom", SimpleTestGenerator)

        ddl = """
        CREATE TABLE test_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100)
        );
        """

        # Test built-in generator
        pydantic_result = create_models(ddl, models_type="pydantic")
        assert "from pydantic import BaseModel" in pydantic_result["code"]

        # Test custom generator
        custom_result = create_models(ddl, models_type="test_custom")
        assert "from test_framework import TestModel" in custom_result["code"]


class TestTypeConverterIntegration:
    """Integration tests for TypeConverter with generators."""

    def test_type_converter_handles_unknown_types(self):
        """Test that TypeConverter passes through unknown types."""

        class UnknownTypeGenerator(BaseGenerator):
            def __init__(self):
                super().__init__()
                self.type_converter = TypeConverter({"varchar": "str", "serial": "int"})

            def generate_model(
                self, table, singular=True, exceptions=None, **kwargs
            ):
                lines = [f"class {table.name}:"]
                for col in table.columns:
                    t = self.type_converter.convert(col.type)
                    lines.append(f"    {col.name}: {t}")
                return "\n".join(lines)

            def create_header(self, tables, **kwargs):
                return ""

        register_generator("test_unknown_types", UnknownTypeGenerator)

        ddl = """
        CREATE TABLE test (
            id SERIAL,
            name VARCHAR(100),
            custom_field CUSTOM_TYPE
        );
        """

        result = create_models(ddl, models_type="test_unknown_types")
        code = result["code"]

        # Known type should be converted
        assert "name: str" in code
        # Unknown type should pass through
        assert "custom_field: custom_type" in code.lower() or "CUSTOM_TYPE" in code
