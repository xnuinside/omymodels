"""Generator registry and utilities."""

import pathlib
from types import ModuleType
from typing import List

from jinja2 import Template

from omymodels.models.dataclass import core as d
from omymodels.models.gino import core as g
from omymodels.models.openapi3 import core as oas3
from omymodels.models.pydantic import core as p
from omymodels.models.pydantic_v2 import core as p2
from omymodels.models.sqlalchemy import core as s
from omymodels.models.sqlalchemy_core import core as sc
from omymodels.models.sqlalchemy_v2 import core as s2
from omymodels.models.sqlmodel import core as sm

# Built-in generator modules
models = {
    "gino": g,
    "pydantic": p,
    "pydantic_v2": p2,
    "dataclass": d,
    "sqlalchemy": s,
    "sqlalchemy_v2": s2,
    "sqlalchemy_core": sc,
    "sqlmodel": sm,
    "openapi3": oas3,
}

supported_models = list(models.keys())


def get_model(models_type: str) -> ModuleType:
    """Get generator module by type name."""
    model = models.get(models_type)
    return model


def get_generator_by_type(models_type: str):
    """Get generator instance by type name.

    Supports both built-in generators and custom registered generators.

    Args:
        models_type: Name of the generator type

    Returns:
        Generator instance

    Raises:
        ValueError: If generator type is not found
    """
    # Check built-in generators first
    model = get_model(models_type)
    if model:
        return getattr(model, "ModelGenerator")()

    # Check custom generators
    from omymodels.plugins import is_custom_generator, get_custom_generator

    if is_custom_generator(models_type):
        generator_class = get_custom_generator(models_type)
        return generator_class()

    # Get list of all available generators for error message
    from omymodels.plugins import list_generators

    available = list(list_generators().keys())

    raise ValueError(
        f"Unsupported models type {models_type!r}. Available generators: {available}"
    )


def get_supported_models() -> List[str]:
    """Get list of all supported model types (built-in and custom).

    Returns:
        List of generator names
    """
    from omymodels.plugins import list_generators

    return list(list_generators().keys())


def render_jinja2_template(models_type: str, models: str, headers: str) -> str:
    """Render Jinja2 template for model output.

    Args:
        models_type: Generator type name
        models: Generated model code
        headers: Generated header/imports code

    Returns:
        Rendered template as string
    """
    template_file = (
        pathlib.Path(__file__).parent / "models" / models_type / f"{models_type}.jinja2"
    )

    # For custom generators without templates, use simple concatenation
    if not template_file.exists():
        return f"{headers}\n{models}"

    with open(template_file) as t:
        template = t.read()
        template = Template(template)
        params = {"models": models, "headers": headers}
        return template.render(**params)
