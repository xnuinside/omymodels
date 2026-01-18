"""OpenAPI 3 schema generator.

Generates OpenAPI 3 schema definitions from DDL or Python models.
"""

import json
from typing import Any, Dict, List, Optional

from table_meta.model import TableMeta

from omymodels.types import (
    boolean_types,
    datetime_types,
    float_types,
    integer_types,
    big_integer_types,
    json_types,
    string_types,
    text_types,
    uuid_types,
    binary_types,
    numeric_types,
)


# Map SQL types to OpenAPI 3 types
TYPE_MAPPING = {
    # String types
    "string": {"type": "string"},
    "str": {"type": "string"},
    # Integer types
    "int": {"type": "integer"},
    "integer": {"type": "integer"},
    "bigint": {"type": "integer", "format": "int64"},
    "smallint": {"type": "integer", "format": "int32"},
    # Float types
    "float": {"type": "number", "format": "float"},
    "double": {"type": "number", "format": "double"},
    "decimal": {"type": "number"},
    "numeric": {"type": "number"},
    # Boolean
    "bool": {"type": "boolean"},
    "boolean": {"type": "boolean"},
    # Date/Time
    "date": {"type": "string", "format": "date"},
    "time": {"type": "string", "format": "time"},
    "datetime": {"type": "string", "format": "date-time"},
    "timestamp": {"type": "string", "format": "date-time"},
    # UUID
    "uuid": {"type": "string", "format": "uuid"},
    # JSON
    "json": {"type": "object"},
    "jsonb": {"type": "object"},
    # Binary
    "bytea": {"type": "string", "format": "byte"},
    "binary": {"type": "string", "format": "binary"},
    "blob": {"type": "string", "format": "binary"},
}


def _add_types_to_mapping(mapping, type_group, oas_type):
    """Add SQL type group to mapping with given OAS type."""
    for sql_type in type_group:
        if sql_type.lower() not in mapping:
            mapping[sql_type.lower()] = oas_type.copy()


def build_type_mapping() -> Dict[str, Dict[str, str]]:
    """Build complete type mapping from SQL type groups."""
    mapping = dict(TYPE_MAPPING)

    type_groups = [
        (string_types, {"type": "string"}),
        (text_types, {"type": "string"}),
        (integer_types, {"type": "integer"}),
        (big_integer_types, {"type": "integer", "format": "int64"}),
        (float_types, {"type": "number", "format": "float"}),
        (numeric_types, {"type": "number"}),
        (boolean_types, {"type": "boolean"}),
        (datetime_types, {"type": "string", "format": "date-time"}),
        (uuid_types, {"type": "string", "format": "uuid"}),
        (json_types, {"type": "object"}),
        (binary_types, {"type": "string", "format": "binary"}),
    ]

    for type_group, oas_type in type_groups:
        _add_types_to_mapping(mapping, type_group, oas_type)

    return mapping


class ModelGenerator:
    """Generator for OpenAPI 3 schema definitions."""

    def __init__(self):
        self.custom_types: Dict[str, Any] = {}
        self.enum_imports: Dict[str, str] = {}
        self.type_mapping = build_type_mapping()
        self.schemas: Dict[str, Dict] = {}
        self.prefix: str = ""

    def _normalize_type(self, type_str: str) -> str:
        """Normalize SQL type for lookup."""
        return type_str.lower().split("(")[0].split("[")[0].strip()

    def _get_oas_type(self, column) -> Dict[str, Any]:
        """Get OpenAPI type for a column."""
        sql_type = self._normalize_type(column.type)

        # Check custom types (enums)
        if sql_type in self.custom_types:
            return {"$ref": f"#/components/schemas/{sql_type}"}

        # Look up in type mapping
        oas_type = self.type_mapping.get(sql_type, {"type": "string"})

        # Handle arrays
        if "[" in column.type:
            return {
                "type": "array",
                "items": dict(oas_type)
            }

        # Handle size for string types
        if oas_type.get("type") == "string" and column.size:
            result = dict(oas_type)
            if isinstance(column.size, int):
                result["maxLength"] = column.size
            return result

        return dict(oas_type)

    def _to_pascal_case(self, name: str) -> str:
        """Convert table name to PascalCase for schema name."""
        # Remove quotes and schema prefix
        name = name.replace('"', '').replace("'", "")
        if "." in name:
            name = name.split(".")[-1]

        # Convert to PascalCase
        words = name.replace("-", "_").split("_")
        return "".join(word.capitalize() for word in words)

    def _parse_default_value(self, prop: Dict, default_str: str) -> None:
        """Parse and set default value based on property type."""
        if default_str.upper() == "NULL":
            return

        prop_type = prop.get("type")
        if prop_type == "integer":
            try:
                prop["default"] = int(default_str)
            except ValueError:
                pass
        elif prop_type == "number":
            try:
                prop["default"] = float(default_str)
            except ValueError:
                pass
        elif prop_type == "boolean":
            prop["default"] = default_str.lower() in ("true", "1")

    def generate_model(
        self,
        table: TableMeta,
        singular: bool = True,
        exceptions: Optional[List[str]] = None,
        **kwargs,
    ) -> str:
        """Generate OpenAPI 3 schema for a table."""
        schema_name = self._to_pascal_case(table.name)

        properties = {}
        required = []

        for column in table.columns:
            prop = self._get_oas_type(column)

            if hasattr(column, "comment") and column.comment:
                prop["description"] = column.comment

            if column.default is not None:
                self._parse_default_value(prop, str(column.default))

            properties[column.name] = prop

            if not column.nullable and column.default is None:
                required.append(column.name)

        schema = {
            "type": "object",
            "properties": properties,
        }

        if required:
            schema["required"] = required

        # Store for later retrieval
        self.schemas[schema_name] = schema

        # Return empty string - actual output is in create_header
        return ""

    def create_header(self, tables: List[TableMeta], **kwargs) -> str:
        """Generate complete OpenAPI 3 components/schemas section."""
        # Generate all schemas first
        for table in tables:
            self.generate_model(table, **kwargs)

        # Add enum schemas
        enum_schemas = {}
        for enum_name, enum_def in self.custom_types.items():
            if hasattr(enum_def, "values"):
                enum_schemas[enum_name] = {
                    "type": "string",
                    "enum": list(enum_def.values)
                }

        # Combine all schemas
        all_schemas = {**enum_schemas, **self.schemas}

        output = {
            "components": {
                "schemas": all_schemas
            }
        }

        return json.dumps(output, indent=2)


def parse_openapi3_schema(schema_content: str) -> List[Dict]:
    """Parse OpenAPI 3 schema and convert to table meta format.

    Args:
        schema_content: OpenAPI 3 schema as JSON or YAML string

    Returns:
        List of parsed model definitions compatible with omymodels
    """
    try:
        schema = json.loads(schema_content)
    except json.JSONDecodeError:
        # Try YAML if JSON fails
        try:
            import yaml
            schema = yaml.safe_load(schema_content)
        except ImportError:
            raise ValueError("Cannot parse schema. Install pyyaml for YAML support.")

    schemas = schema.get("components", {}).get("schemas", {})
    if not schemas:
        # Try top-level definitions (Swagger 2.0 compatibility)
        schemas = schema.get("definitions", {})

    models = []

    for name, definition in schemas.items():
        if definition.get("type") == "object":
            attrs = []
            properties = definition.get("properties", {})
            required_fields = set(definition.get("required", []))

            for prop_name, prop_def in properties.items():
                attr = {
                    "name": prop_name,
                    "type": _oas_to_python_type(prop_def),
                    "default": prop_def.get("default"),
                }

                # Set properties based on required
                attr["properties"] = {
                    "nullable": prop_name not in required_fields
                }

                attrs.append(attr)

            models.append({
                "name": name,
                "attrs": attrs,
                "parents": ["BaseModel"],  # Default to Pydantic-style
                "properties": {},
            })

        elif "enum" in definition:
            # Handle enum types
            models.append({
                "name": name,
                "attrs": [{"name": v, "value": v} for v in definition["enum"]],
                "parents": ["str", "Enum"],
                "properties": {},
            })

    return models


def _oas_to_python_type(prop_def: Dict) -> str:
    """Convert OpenAPI type definition to Python type string."""
    oas_type = prop_def.get("type", "string")
    oas_format = prop_def.get("format")

    # Handle refs
    if "$ref" in prop_def:
        ref = prop_def["$ref"]
        return ref.split("/")[-1]

    # Handle arrays
    if oas_type == "array":
        items = prop_def.get("items", {})
        item_type = _oas_to_python_type(items)
        return f"List[{item_type}]"

    # Type mapping
    type_map = {
        ("string", None): "str",
        ("string", "date"): "datetime.date",
        ("string", "date-time"): "datetime.datetime",
        ("string", "time"): "datetime.time",
        ("string", "uuid"): "uuid.UUID",
        ("string", "byte"): "bytes",
        ("string", "binary"): "bytes",
        ("integer", None): "int",
        ("integer", "int32"): "int",
        ("integer", "int64"): "int",
        ("number", None): "float",
        ("number", "float"): "float",
        ("number", "double"): "float",
        ("boolean", None): "bool",
        ("object", None): "dict",
    }

    return type_map.get((oas_type, oas_format), "str")
