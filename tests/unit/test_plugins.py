"""Unit tests for the plugin system."""

import pytest

from omymodels import (
    BaseGenerator,
    list_generators,
    register_generator,
    unregister_generator,
)
from omymodels.plugins import (
    _custom_generators,
    get_all_custom_generators,
    get_custom_generator,
    is_custom_generator,
)


class ValidGenerator(BaseGenerator):
    """Valid test generator with required methods."""

    def generate_model(self, table, singular=True, exceptions=None, **kwargs):
        return f"class {table.name}:\n    pass"

    def create_header(self, tables, **kwargs):
        return "# Header\n"


class AnotherValidGenerator(BaseGenerator):
    """Another valid test generator."""

    def generate_model(self, table, **kwargs):
        return ""

    def create_header(self, tables, **kwargs):
        return ""


@pytest.fixture(autouse=True)
def cleanup_custom_generators():
    """Clean up custom generators before and after each test."""
    # Store original state
    original = dict(_custom_generators)
    _custom_generators.clear()
    yield
    # Restore original state
    _custom_generators.clear()
    _custom_generators.update(original)


class TestRegisterGenerator:
    """Tests for register_generator function."""

    def test_register_valid_generator(self):
        """Test registering a valid generator."""
        register_generator("test_gen", ValidGenerator)
        assert is_custom_generator("test_gen")
        assert get_custom_generator("test_gen") is ValidGenerator

    def test_register_multiple_generators(self):
        """Test registering multiple generators."""
        register_generator("gen1", ValidGenerator)
        register_generator("gen2", AnotherValidGenerator)

        assert is_custom_generator("gen1")
        assert is_custom_generator("gen2")
        assert len(get_all_custom_generators()) == 2

    def test_register_non_subclass_raises_type_error(self):
        """Test that registering a non-BaseGenerator subclass raises TypeError."""

        class NotAGenerator:
            pass

        with pytest.raises(TypeError, match="must inherit from BaseGenerator"):
            register_generator("bad_gen", NotAGenerator)

    def test_register_non_class_raises_type_error(self):
        """Test that registering a non-class raises TypeError."""
        with pytest.raises(TypeError, match="must inherit from BaseGenerator"):
            register_generator("bad_gen", "not a class")

    def test_register_incomplete_generator_cannot_be_instantiated(self):
        """Test that incomplete generator (abstract methods not implemented) fails at instantiation."""

        # Note: Python's ABC mechanism means subclasses that don't implement
        # abstract methods will raise TypeError at instantiation, not at registration.
        # The register_generator function validates that methods are callable on the class.
        class IncompleteGenerator(BaseGenerator):
            # Only implements create_header, not generate_model
            def create_header(self, tables, **kwargs):
                return ""

        # Registration succeeds because the abstract method exists (even if not properly implemented)
        # But instantiation should fail
        register_generator("incomplete_test", IncompleteGenerator)

        with pytest.raises(TypeError):
            IncompleteGenerator()

    def test_register_invalid_name_raises_value_error(self):
        """Test that invalid generator name raises ValueError."""
        with pytest.raises(ValueError, match="Invalid generator name"):
            register_generator("invalid-name", ValidGenerator)

        with pytest.raises(ValueError, match="Invalid generator name"):
            register_generator("123invalid", ValidGenerator)

        with pytest.raises(ValueError, match="Invalid generator name"):
            register_generator("", ValidGenerator)

    def test_register_builtin_name_raises_value_error(self):
        """Test that registering with a built-in name raises ValueError."""
        with pytest.raises(ValueError, match="Cannot override built-in generator"):
            register_generator("gino", ValidGenerator)

        with pytest.raises(ValueError, match="Cannot override built-in generator"):
            register_generator("pydantic", ValidGenerator)


class TestUnregisterGenerator:
    """Tests for unregister_generator function."""

    def test_unregister_existing_generator(self):
        """Test unregistering an existing generator."""
        register_generator("to_remove", ValidGenerator)
        assert is_custom_generator("to_remove")

        result = unregister_generator("to_remove")
        assert result is True
        assert not is_custom_generator("to_remove")

    def test_unregister_nonexistent_generator(self):
        """Test unregistering a non-existent generator returns False."""
        result = unregister_generator("nonexistent")
        assert result is False


class TestGetCustomGenerator:
    """Tests for get_custom_generator function."""

    def test_get_existing_generator(self):
        """Test getting an existing custom generator."""
        register_generator("my_gen", ValidGenerator)
        result = get_custom_generator("my_gen")
        assert result is ValidGenerator

    def test_get_nonexistent_generator_raises_key_error(self):
        """Test getting a non-existent generator raises KeyError."""
        with pytest.raises(KeyError, match="Custom generator not found"):
            get_custom_generator("nonexistent")


class TestListGenerators:
    """Tests for list_generators function."""

    def test_list_includes_builtin_generators(self):
        """Test that list_generators includes built-in generators."""
        result = list_generators()

        assert "gino" in result
        assert "pydantic" in result
        assert "pydantic_v2" in result
        assert "dataclass" in result
        assert "sqlalchemy" in result

        # All built-ins should be marked as "builtin"
        assert result["gino"] == "builtin"
        assert result["pydantic"] == "builtin"

    def test_list_includes_custom_generators(self):
        """Test that list_generators includes custom generators."""
        register_generator("my_custom", ValidGenerator)
        result = list_generators()

        assert "my_custom" in result
        assert result["my_custom"] == "custom"


class TestIsCustomGenerator:
    """Tests for is_custom_generator function."""

    def test_is_custom_returns_true_for_custom(self):
        """Test is_custom_generator returns True for custom generators."""
        register_generator("custom_test", ValidGenerator)
        assert is_custom_generator("custom_test") is True

    def test_is_custom_returns_false_for_builtin(self):
        """Test is_custom_generator returns False for built-in generators."""
        assert is_custom_generator("gino") is False
        assert is_custom_generator("pydantic") is False

    def test_is_custom_returns_false_for_nonexistent(self):
        """Test is_custom_generator returns False for non-existent generators."""
        assert is_custom_generator("nonexistent") is False


class TestGetAllCustomGenerators:
    """Tests for get_all_custom_generators function."""

    def test_returns_empty_dict_when_no_custom(self):
        """Test returns empty dict when no custom generators registered."""
        result = get_all_custom_generators()
        assert result == {}

    def test_returns_all_custom_generators(self):
        """Test returns all registered custom generators."""
        register_generator("gen1", ValidGenerator)
        register_generator("gen2", AnotherValidGenerator)

        result = get_all_custom_generators()
        assert len(result) == 2
        assert result["gen1"] is ValidGenerator
        assert result["gen2"] is AnotherValidGenerator

    def test_returns_copy_not_original(self):
        """Test that returned dict is a copy."""
        register_generator("test_gen", ValidGenerator)
        result = get_all_custom_generators()
        result.clear()

        # Original should still have the generator
        assert is_custom_generator("test_gen")
