""" module that contain list of available providers and methods to add them """
from .base.generator import BaseGenerator
from .base.parser import BaseParser
from typing import List


class Providers:

    generators: List[BaseGenerator] = []
    parsers: List[BaseParser] = []

    def find_by_name(self, class_type: str, name: str):
        field = getattr(self, class_type)
        name = [value.__class__.name for value in field]
        if len(name) == 0:
            raise ValueError(f"Provider of type '{class_type}' with name {name} "
                             "does not exits in list of O!MyModels {class_type}. "
                             f"Available variants: {field}")

    def add_new(self, provider: object):
        if isinstance(provider, BaseParser):
            self.parsers.append(provider)
        elif isinstance(provider, BaseGenerator):
            self.generators.append(provider)
        else:
            raise ValueError(f'Provider should be created with inheritance from one of classes: '
                            'omymodels.base.BaseParser or omymodels.base.BaseGenerator')


providers = Providers()
