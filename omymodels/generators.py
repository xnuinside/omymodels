import pathlib
from types import ModuleType
from jinja2 import Template

from omymodels.models.gino import core as g
from omymodels.models.pydantic import core as p
from omymodels.models.dataclass import core as d
from omymodels.models.sqlalchemy import core as s
from omymodels.models.sqlalchemy_core import core as sc


models = {
    "gino": g,
    "pydantic": p,
    "dataclass": d,
    "sqlalchemy": s,
    "sqlalchemy_core": sc,
}


supported_models = list(models.keys())


def get_model(models_type: str) -> ModuleType:
    model = models.get(models_type)
    return model


def get_generator_by_type(models_type: str):
    model = get_model(models_type)
    if not model:
        raise ValueError(
            f"Unsupported models type {models_type}. Possible variants: {supported_models}"
        )
    return getattr(model, "ModelGenerator")()


def render_jinja2_template(models_type: str, models: str, headers: str) -> str:
    template_file = (
        pathlib.Path(__file__).parent / "models" / models_type / f"{models_type}.jinja2"
    )

    with open(template_file) as t:
        template = t.read()
        template = Template(template)
        params = {"models": models, "headers": headers}
        return template.render(**params)
