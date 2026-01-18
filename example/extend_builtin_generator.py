"""Example: Extending a built-in generator.

This example shows how to customize an existing generator
by inheriting from it and overriding specific behavior.
"""

from omymodels import create_models, register_generator

# Import the built-in generator you want to extend
from omymodels.models.pydantic_v2.core import ModelGenerator as PydanticV2Generator


class CustomPydanticGenerator(PydanticV2Generator):
    """Pydantic v2 generator with custom JSON type handling.

    This example changes JSON fields to use a custom JsonData type
    instead of the default dict | list.
    """

    def __init__(self):
        super().__init__()
        # Add custom import
        self.custom_json_import = True

    def get_not_custom_type(self, column):
        """Override to use custom type for JSON fields."""
        _type = super().get_not_custom_type(column)

        # Replace dict | list with our custom JsonData type
        if _type == "dict | list":
            return "JsonData"

        return _type

    def create_header(self, *args, **kwargs):
        """Add custom import to header."""
        header = super().create_header(*args, **kwargs)

        # Prepend our custom import
        if self.custom_json_import:
            custom_import = "from my_types import JsonData\n"
            return custom_import + header

        return header


# Register the custom generator
register_generator("my_pydantic", CustomPydanticGenerator)


if __name__ == "__main__":
    ddl = """
    CREATE TABLE config (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        settings JSON NOT NULL,
        metadata JSONB
    );
    """

    # Use custom generator
    result = create_models(ddl, models_type="my_pydantic")
    print(result["code"])

    # Output:
    # from my_types import JsonData
    # from __future__ import annotations
    #
    # from pydantic import BaseModel
    #
    #
    # class Config(BaseModel):
    #
    #     id: int
    #     name: str
    #     settings: JsonData
    #     metadata: JsonData | None = None
