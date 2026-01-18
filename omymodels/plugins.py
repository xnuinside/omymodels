"""Plugin system for custom generators.

Allows users to register their own model generators without forking the repository.
"""

import sys
from typing import Dict, List, Type

from omymodels.generation.base import BaseGenerator

# Registry of custom generators
_custom_generators: Dict[str, Type[BaseGenerator]] = {}


def register_generator(name: str, generator_class: Type[BaseGenerator]) -> None:
    """Register a custom generator.

    Args:
        name: Unique generator name (e.g., "my_orm", "custom_pydantic")
        generator_class: Generator class inheriting from BaseGenerator

    Raises:
        TypeError: If generator_class doesn't inherit from BaseGenerator
        TypeError: If generator_class is missing required methods
        ValueError: If name is not a valid identifier
        ValueError: If name conflicts with a built-in generator

    Example:
        from omymodels import register_generator
        from omymodels.generation import BaseGenerator

        class MyORMGenerator(BaseGenerator):
            def generate_model(self, table, **kwargs):
                ...
            def create_header(self, tables, **kwargs):
                ...

        register_generator("my_orm", MyORMGenerator)
    """
    # Validate inheritance
    if not isinstance(generator_class, type) or not issubclass(
        generator_class, BaseGenerator
    ):
        raise TypeError(
            f"Generator must inherit from BaseGenerator, got {generator_class}"
        )

    # Validate required methods
    required_methods = ["generate_model", "create_header"]
    for method in required_methods:
        if not callable(getattr(generator_class, method, None)):
            raise TypeError(f"Generator missing required method: {method}")

    # Validate name
    if not name.isidentifier():
        raise ValueError(f"Invalid generator name: {name!r}. Must be a valid identifier.")

    # Check for conflicts with built-in generators
    from omymodels.generators import models as builtin_generators

    if name in builtin_generators:
        raise ValueError(
            f"Cannot override built-in generator: {name!r}. Use a different name."
        )

    _custom_generators[name] = generator_class


def unregister_generator(name: str) -> bool:
    """Remove a custom generator.

    Args:
        name: Name of the generator to remove

    Returns:
        True if generator was removed, False if not found
    """
    return _custom_generators.pop(name, None) is not None


def get_custom_generator(name: str) -> Type[BaseGenerator]:
    """Get a custom generator by name.

    Args:
        name: Generator name

    Returns:
        Generator class

    Raises:
        KeyError: If generator not found
    """
    if name not in _custom_generators:
        raise KeyError(f"Custom generator not found: {name!r}")
    return _custom_generators[name]


def list_generators() -> Dict[str, str]:
    """List all available generators (built-in and custom).

    Returns:
        Dictionary mapping generator names to their type (builtin/custom)
    """
    from omymodels.generators import models as builtin_generators

    result = {name: "builtin" for name in builtin_generators}
    result.update({name: "custom" for name in _custom_generators})
    return result


def is_custom_generator(name: str) -> bool:
    """Check if a generator name refers to a custom generator.

    Args:
        name: Generator name

    Returns:
        True if custom generator
    """
    return name in _custom_generators


def get_all_custom_generators() -> Dict[str, Type[BaseGenerator]]:
    """Get all registered custom generators.

    Returns:
        Dictionary of custom generator name to class
    """
    return dict(_custom_generators)


def discover_plugins() -> None:
    """Auto-discover generators from entry points.

    Looks for entry points in the "omymodels.generators" group.

    Example pyproject.toml:
        [project.entry-points."omymodels.generators"]
        peewee = "my_package.generators:PeeweeGenerator"
    """
    try:
        if sys.version_info >= (3, 10):
            from importlib.metadata import entry_points

            eps = entry_points(group="omymodels.generators")
        else:
            from importlib.metadata import entry_points

            all_eps = entry_points()
            eps = all_eps.get("omymodels.generators", [])

        for ep in eps:
            try:
                generator_class = ep.load()
                register_generator(ep.name, generator_class)
            except Exception:
                # Skip failed plugins silently
                pass
    except Exception:
        # Entry points not available
        pass


# Auto-discover plugins on import
discover_plugins()
