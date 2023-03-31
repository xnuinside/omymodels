from .provider import BaseProvider
from .mixins import EqualByNameMixIn
from typing import Optional


class BaseGenerator(BaseProvider):

    name = 'define-name-of-your-generator'

    def run(self, input, params):
        pass


class Generator(EqualByNameMixIn):
    def __init__(self, name: str, params: Optional[dict] = None) -> None:

        self.generator = self.get_class_by_name()
        self.name = name
        self.params = params
    
    def get_class_by_name(self):
        pass

    def run(self):
        pass
