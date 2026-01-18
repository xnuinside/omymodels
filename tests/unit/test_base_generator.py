"""Unit tests for the base generator classes."""

import pytest

from omymodels.generation import BaseGenerator, DataModelGenerator, ORMGenerator


class ConcreteGenerator(BaseGenerator):
    """Concrete implementation of BaseGenerator for testing."""

    def generate_model(self, table, singular=True, exceptions=None, **kwargs):
        return f"class {table.name}:\n    pass"

    def create_header(self, tables, **kwargs):
        return "# Header\n"


class TestBaseGenerator:
    """Tests for BaseGenerator abstract class."""

    def test_init_sets_empty_custom_types(self):
        """Test that init sets empty custom_types dict."""
        gen = ConcreteGenerator()
        assert gen.custom_types == {}

    def test_init_sets_empty_prefix(self):
        """Test that init sets empty prefix."""
        gen = ConcreteGenerator()
        assert gen.prefix == ""

    def test_add_custom_type(self):
        """Test adding a custom type."""
        gen = ConcreteGenerator()
        gen.add_custom_type("MyEnum", "EnumType")

        assert "MyEnum" in gen.custom_types
        assert gen.custom_types["MyEnum"] == "EnumType"

    def test_add_custom_type_tuple(self):
        """Test adding a custom type as tuple."""
        gen = ConcreteGenerator()
        gen.add_custom_type("MyEnum", ("OriginalType", "MappedType"))

        assert gen.custom_types["MyEnum"] == ("OriginalType", "MappedType")

    def test_get_custom_type_simple(self):
        """Test getting a simple custom type (non-tuple)."""
        gen = ConcreteGenerator()
        gen.add_custom_type("MyEnum", "EnumType")

        # Simple types return None (only tuples return mapped value)
        result = gen.get_custom_type("MyEnum")
        assert result is None

    def test_get_custom_type_tuple(self):
        """Test getting a custom type from tuple."""
        gen = ConcreteGenerator()
        gen.add_custom_type("MyEnum", ("OriginalType", "MappedType"))

        result = gen.get_custom_type("MyEnum")
        assert result == "MappedType"

    def test_get_custom_type_nonexistent(self):
        """Test getting a non-existent custom type."""
        gen = ConcreteGenerator()
        result = gen.get_custom_type("NonExistent")
        assert result is None

    def test_reset_clears_custom_types(self):
        """Test that reset clears custom_types."""
        gen = ConcreteGenerator()
        gen.add_custom_type("Type1", "Value1")
        gen.add_custom_type("Type2", "Value2")

        gen.reset()

        assert gen.custom_types == {}

    def test_cannot_instantiate_abstract_base(self):
        """Test that BaseGenerator cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseGenerator()


class TestBaseGeneratorInheritance:
    """Tests for proper inheritance behavior."""

    def test_subclass_must_implement_generate_model(self):
        """Test that subclass without generate_model raises error."""

        class IncompleteGenerator(BaseGenerator):
            def create_header(self, tables, **kwargs):
                return ""

        with pytest.raises(TypeError, match="generate_model"):
            IncompleteGenerator()

    def test_subclass_must_implement_create_header(self):
        """Test that subclass without create_header raises error."""

        class IncompleteGenerator(BaseGenerator):
            def generate_model(self, table, **kwargs):
                return ""

        with pytest.raises(TypeError, match="create_header"):
            IncompleteGenerator()

    def test_complete_subclass_can_be_instantiated(self):
        """Test that complete subclass can be instantiated."""
        gen = ConcreteGenerator()
        assert isinstance(gen, BaseGenerator)


class TestORMGenerator:
    """Tests for ORMGenerator base class."""

    def test_orm_generator_cannot_be_instantiated(self):
        """Test that ORMGenerator cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ORMGenerator()

    def test_orm_generator_has_prepare_column_default(self):
        """Test that ORMGenerator has prepare_column_default method."""
        assert hasattr(ORMGenerator, "prepare_column_default")

    def test_orm_generator_has_build_orm_header(self):
        """Test that ORMGenerator has build_orm_header method."""
        assert hasattr(ORMGenerator, "build_orm_header")


class TestDataModelGenerator:
    """Tests for DataModelGenerator base class."""

    def test_datamodel_generator_cannot_be_instantiated(self):
        """Test that DataModelGenerator cannot be instantiated directly."""
        with pytest.raises(TypeError):
            DataModelGenerator()

    def test_datamodel_generator_has_get_python_type(self):
        """Test that DataModelGenerator has get_python_type method."""
        assert hasattr(DataModelGenerator, "get_python_type")

    def test_datamodel_generator_has_format_default_value(self):
        """Test that DataModelGenerator has format_default_value method."""
        assert hasattr(DataModelGenerator, "format_default_value")

    def test_datamodel_generator_has_build_header_imports(self):
        """Test that DataModelGenerator has build_header_imports method."""
        assert hasattr(DataModelGenerator, "build_header_imports")
