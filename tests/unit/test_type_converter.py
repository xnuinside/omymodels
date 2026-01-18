"""Unit tests for the TypeConverter class."""

from omymodels.types import TypeConverter


class TestTypeConverterBasics:
    """Basic TypeConverter functionality tests."""

    def test_init_with_simple_mapping(self):
        """Test initialization with a simple type mapping."""
        mapping = {
            "varchar": "str",
            "integer": "int",
            "boolean": "bool",
        }
        converter = TypeConverter(mapping)

        assert converter.mapping == mapping
        assert converter.prefix == ""

    def test_init_with_prefix(self):
        """Test initialization with a prefix."""
        mapping = {"varchar": "String"}
        converter = TypeConverter(mapping, prefix="db.")

        assert converter.prefix == "db."

    def test_convert_exact_match(self):
        """Test converting an exact type match."""
        mapping = {"varchar": "str", "integer": "int"}
        converter = TypeConverter(mapping)

        assert converter.convert("varchar") == "str"
        assert converter.convert("integer") == "int"

    def test_convert_case_insensitive(self):
        """Test that conversion is case-insensitive."""
        mapping = {"varchar": "str", "INTEGER": "int"}
        converter = TypeConverter(mapping)

        assert converter.convert("VARCHAR") == "str"
        assert converter.convert("Varchar") == "str"
        assert converter.convert("integer") == "int"
        assert converter.convert("INTEGER") == "int"

    def test_convert_strips_size_specifier(self):
        """Test that size specifiers are stripped during conversion."""
        mapping = {"varchar": "str", "numeric": "Decimal"}
        converter = TypeConverter(mapping)

        assert converter.convert("varchar(100)") == "str"
        assert converter.convert("VARCHAR(255)") == "str"
        assert converter.convert("numeric(10, 2)") == "Decimal"

    def test_convert_strips_array_notation(self):
        """Test that array notation is stripped during conversion."""
        mapping = {"integer": "int", "varchar": "str"}
        converter = TypeConverter(mapping)

        assert converter.convert("integer[]") == "int"
        assert converter.convert("varchar[10]") == "str"

    def test_convert_unknown_type_returns_original(self):
        """Test that unknown types are returned as-is."""
        mapping = {"varchar": "str"}
        converter = TypeConverter(mapping)

        assert converter.convert("custom_type") == "custom_type"
        assert converter.convert("UNKNOWN") == "UNKNOWN"


class TestTypeConverterWithSize:
    """Tests for with_size method."""

    def test_with_size_none_returns_type(self):
        """Test with_size returns original type when size is None."""
        converter = TypeConverter({})
        assert converter.with_size("String", None) == "String"

    def test_with_size_integer(self):
        """Test with_size with integer size."""
        converter = TypeConverter({})
        assert converter.with_size("String", 100) == "String(100)"
        assert converter.with_size("VARCHAR", 255) == "VARCHAR(255)"

    def test_with_size_tuple(self):
        """Test with_size with tuple (precision, scale)."""
        converter = TypeConverter({})
        assert converter.with_size("Numeric", (10, 2)) == "Numeric(10, 2)"
        assert converter.with_size("DECIMAL", (15, 4)) == "DECIMAL(15, 4)"


class TestTypeConverterTypeChecks:
    """Tests for type checking methods."""

    def test_is_datetime_true_for_datetime_types(self):
        """Test is_datetime returns True for datetime types."""
        converter = TypeConverter({})

        assert converter.is_datetime("TIMESTAMP") is True
        assert converter.is_datetime("DATE") is True
        assert converter.is_datetime("TIME") is True
        assert converter.is_datetime("DATETIME") is True

    def test_is_datetime_false_for_non_datetime(self):
        """Test is_datetime returns False for non-datetime types."""
        converter = TypeConverter({})

        assert converter.is_datetime("varchar") is False
        assert converter.is_datetime("integer") is False
        assert converter.is_datetime("boolean") is False

    def test_is_json_true_for_json_types(self):
        """Test is_json returns True for JSON types."""
        converter = TypeConverter({})

        assert converter.is_json("json") is True
        assert converter.is_json("jsonb") is True

    def test_is_json_false_for_non_json(self):
        """Test is_json returns False for non-JSON types."""
        converter = TypeConverter({})

        assert converter.is_json("varchar") is False
        assert converter.is_json("text") is False


class TestTypeConverterUpdate:
    """Tests for update method."""

    def test_update_adds_new_types(self):
        """Test update adds new type mappings."""
        mapping = {"varchar": "str"}
        converter = TypeConverter(mapping)

        converter.update({"integer": "int"})

        assert converter.convert("varchar") == "str"
        assert converter.convert("integer") == "int"

    def test_update_overrides_existing_types(self):
        """Test update can override existing type mappings."""
        mapping = {"varchar": "str"}
        converter = TypeConverter(mapping)

        converter.update({"varchar": "Text"})

        assert converter.convert("varchar") == "Text"

    def test_update_rebuilds_lookup(self):
        """Test that update rebuilds the lookup table."""
        mapping = {"VARCHAR": "str"}
        converter = TypeConverter(mapping)

        # Original lookup should work
        assert converter.convert("varchar") == "str"

        # Add with different case
        converter.update({"INTEGER": "int"})

        # Both should work (case-insensitive)
        assert converter.convert("varchar") == "str"
        assert converter.convert("integer") == "int"


class TestTypeConverterGet:
    """Tests for get method."""

    def test_get_existing_type(self):
        """Test get returns type for existing mapping."""
        mapping = {"varchar": "str", "integer": "int"}
        converter = TypeConverter(mapping)

        assert converter.get("varchar") == "str"
        assert converter.get("integer") == "int"

    def test_get_with_default(self):
        """Test get returns default for unknown type."""
        converter = TypeConverter({})

        assert converter.get("unknown", "default_type") == "default_type"
        assert converter.get("custom", None) is None

    def test_get_strips_size(self):
        """Test get strips size specifier."""
        mapping = {"varchar": "str"}
        converter = TypeConverter(mapping)

        assert converter.get("varchar(100)") == "str"

    def test_get_case_insensitive(self):
        """Test get is case-insensitive."""
        mapping = {"VARCHAR": "str"}
        converter = TypeConverter(mapping)

        assert converter.get("varchar") == "str"
        assert converter.get("VARCHAR") == "str"


class TestTypeConverterRealWorldMappings:
    """Tests with real-world type mappings."""

    def test_pydantic_type_mapping(self):
        """Test with Pydantic-like type mapping."""
        mapping = {
            "varchar": "str",
            "character varying": "str",
            "text": "str",
            "integer": "int",
            "bigint": "int",
            "smallint": "int",
            "boolean": "bool",
            "float": "float",
            "double": "float",
            "decimal": "float",
            "numeric": "float",
            "timestamp": "datetime.datetime",
            "date": "datetime.date",
            "time": "datetime.time",
            "uuid": "uuid.UUID",
            "json": "dict",
            "jsonb": "dict",
        }
        converter = TypeConverter(mapping)

        assert converter.convert("VARCHAR(255)") == "str"
        assert converter.convert("character varying") == "str"
        assert converter.convert("INTEGER") == "int"
        assert converter.convert("bigint") == "int"
        assert converter.convert("boolean") == "bool"
        assert converter.convert("numeric(10,2)") == "float"
        assert converter.convert("timestamp") == "datetime.datetime"
        assert converter.convert("JSONB") == "dict"

    def test_gino_type_mapping(self):
        """Test with Gino-like type mapping."""
        mapping = {
            "varchar": "String",
            "character varying": "String",
            "text": "Text",
            "integer": "Integer",
            "bigint": "BigInteger",
            "boolean": "Boolean",
            "timestamp": "TIMESTAMP",
            "json": "JSON",
            "jsonb": "JSONB",
        }
        converter = TypeConverter(mapping, prefix="db.")

        assert converter.convert("varchar(100)") == "String"
        assert converter.convert("INTEGER") == "Integer"
        assert converter.convert("jsonb") == "JSONB"
