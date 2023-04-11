from typing import Any
from .base.config import Config

""" module that contain list of available providers and methods to work with them """
from .base.generator import BaseGenerator
from .base.parser import BaseParser
from typing import List, Union


class ProvidersCatalog:

    generators: List[BaseGenerator] = []
    parsers: List[BaseParser] = []

    def find_by_name(self, provider_type: str, name: str, no_error: bool = False) -> Union[BaseGenerator, BaseParser]:
        field = getattr(self, f'{provider_type}s', None)
        if field is None:
            raise ValueError("provider_type argument can be only one of ['generator', 'parser']")

        provider_class_list = [value for value in field if value.name == name]

        provider_class = None
        if len(provider_class_list) == 0:
            if not no_error:
                raise ValueError(f"Provider of type '{provider_type}' with name {name} "
                                "does not exits in list of O!MyModels {class_type}. "
                                f"Available variants: {field}")
        else:
            provider_class = provider_class_list[0]
        return provider_class
    
    def add_new(self, provider: Union[BaseGenerator, BaseParser]) -> None:
        if isinstance(provider, type):
            if issubclass(provider, BaseParser):
                provider_type = 'parser'
            elif issubclass(provider, BaseGenerator):
                provider_type = 'generator'
            else:
                raise ValueError(f'Provider should be created with inheritance from one of classes: '
                                'omymodels.base.BaseParser or omymodels.base.BaseGenerator')
            
            provider_witn_same_name = self.find_by_name(provider_type, provider.name, no_error=True)
            if provider_witn_same_name:
                raise ValueError(f'Provider with name {provider.name} already exists in O!MyModels parsers.' 
                                 'Please change the name of provider, that you tries to add')
            providers_list = getattr(self, f'{provider_type}s')
            providers_list.append(provider)

        else:
            raise ValueError(f'Provider should be a class, not object or any other type. Pure python class, '
                            'that inherit from omymodels.base.BaseParser or omymodels.base.BaseGenerator')



def main(*args, **kwargs):
    config = Config(*args, **kwargs)
    # get settings
    # get model generator

    # get input
    # parsing step
    # Parser -> ParsedInput

    # ParsedInput -> SourceInput convert input to TableMeta

    # parsing step
    # SourceInput -> FormattedInput
    # call ModelGenerator - convert InputSource

