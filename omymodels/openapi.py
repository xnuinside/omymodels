"""OpenAPI 3 schema parsing and conversion.

This module provides functions to parse OpenAPI 3 schemas and convert them
to Python model code (Pydantic, Dataclass, SQLAlchemy, etc.).
"""

import json
from typing import Dict

from table_meta.model import Column, TableMeta

from omymodels.generators import get_generator_by_type, render_jinja2_template
from omymodels.helpers import add_custom_types_to_generator
from omymodels.models.enum import core as enum


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
        return f"{item_type}[]"

    # Type mapping
    type_map = {
        ("string", None): "varchar",
        ("string", "date"): "date",
        ("string", "date-time"): "timestamp",
        ("string", "time"): "time",
        ("string", "uuid"): "uuid",
        ("string", "byte"): "bytea",
        ("string", "binary"): "binary",
        ("integer", None): "integer",
        ("integer", "int32"): "integer",
        ("integer", "int64"): "bigint",
        ("number", None): "float",
        ("number", "float"): "float",
        ("number", "double"): "double",
        ("boolean", None): "boolean",
        ("object", None): "jsonb",
    }

    return type_map.get((oas_type, oas_format), "varchar")


def _parse_openapi3_schema(schema_content: str) -> tuple:
    """Parse OpenAPI 3 schema and convert to TableMeta format.

    Args:
        schema_content: OpenAPI 3 schema as JSON or YAML string

    Returns:
        Tuple of (tables, types) for use with generators
    """
    try:
        schema = json.loads(schema_content)
    except json.JSONDecodeError:
        # Try YAML if JSON fails
        try:
            import yaml
            schema = yaml.safe_load(schema_content)
        except ImportError:
            raise ValueError(
                "Cannot parse YAML schema. Install pyyaml: pip install pyyaml"
            )

    schemas = schema.get("components", {}).get("schemas", {})
    if not schemas:
        # Try top-level definitions (Swagger 2.0 compatibility)
        schemas = schema.get("definitions", {})

    tables = []
    types = []

    for name, definition in schemas.items():
        if definition.get("type") == "object":
            properties = definition.get("properties", {})
            required_fields = set(definition.get("required", []))

            columns = []
            for prop_name, prop_def in properties.items():
                col_type = _oas_to_python_type(prop_def)
                nullable = prop_name not in required_fields
                default = prop_def.get("default")

                col = Column(
                    name=prop_name,
                    type=col_type,
                    nullable=nullable,
                    default=default,
                    size=prop_def.get("maxLength"),
                )
                columns.append(col)

            table = TableMeta(
                name=name.lower() + "s",  # Pluralize for table name
                table_name=name.lower() + "s",
                columns=columns,
                primary_key=[],
                properties={"indexes": []},
            )
            tables.append(table)

        elif "enum" in definition:
            # Handle enum types
            from table_meta import Type

            enum_type = Type(
                type_name=name,
                base_type="str",
                values=definition["enum"],
            )
            types.append(enum_type)

    return tables, types


def create_models_from_openapi3(
    schema_content: str,
    models_type: str = "pydantic",
    **kwargs,
) -> str:
    """Create Python models from OpenAPI 3 schema.

    Args:
        schema_content: OpenAPI 3 schema as JSON or YAML string
        models_type: Target model type (pydantic, pydantic_v2, dataclass,
                     sqlalchemy, gino, sqlmodel)
        **kwargs: Additional arguments passed to the generator

    Returns:
        Generated Python model code as string

    Example:
        >>> schema = '''
        ... {
        ...   "components": {
        ...     "schemas": {
        ...       "User": {
        ...         "type": "object",
        ...         "properties": {
        ...           "id": {"type": "integer"},
        ...           "name": {"type": "string"},
        ...           "email": {"type": "string", "format": "email"}
        ...         },
        ...         "required": ["id", "name"]
        ...       }
        ...     }
        ...   }
        ... }
        ... '''
        >>> result = create_models_from_openapi3(schema, models_type="pydantic_v2")
        >>> print(result)
    """
    tables, types = _parse_openapi3_schema(schema_content)

    if not tables and not types:
        raise ValueError("No schemas found in OpenAPI specification")

    generator = get_generator_by_type(models_type)
    models_str = ""
    header = ""

    if types:
        types_generator = enum.ModelGenerator(types)
        models_str += types_generator.create_types()
        header += types_generator.create_header()

    if tables:
        add_custom_types_to_generator(types, generator)

        for table in tables:
            models_str += generator.generate_model(table, **kwargs)
        header += generator.create_header(tables, **kwargs)
    else:
        header += enum.create_header(generator.enum_imports)
        models_type = "enum"

    output = render_jinja2_template(models_type, models_str, header)
    return output
