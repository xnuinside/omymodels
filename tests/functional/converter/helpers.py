"""framework for fast testing models conversion based on ddl to model result models from one
ddl must produce same output as model created directly from ddl
"""

from typing import List, Tuple

from omymodels import create_models
from omymodels.generators import supported_models


def generate_model_code(ddl: str, models_type: str) -> str:
    return create_models(ddl, models_type=models_type)["code"]


def models_generator(ddl: str):
    models_code_from_ddl = {}

    for model_type in supported_models:
        model_code = generate_model_code(ddl, models_type=model_type)
        models_code_from_ddl[model_type] = model_code

    return models_code_from_ddl


def generate_params_for_converter(ddl: str) -> List[Tuple[str]]:
    """return params for test fixture with data
    base_model_type, target_model_type, base_model_code(from ddl), expected(from ddl)
    """
    models_from_ddl = models_generator(ddl)
    params = []
    for base_model_name, code in models_from_ddl.items():
        other_models = [model for model in supported_models if model != base_model_name]
        for target_model in other_models:
            params.append(
                (base_model_name, target_model, code, models_from_ddl.get(target_model))
            )
    return params
