from .mixins import EqualByNameMixIn
from typing import Optional
from .provider import BaseProvider


class BaseParser(BaseProvider):

    name = 'base-parser'

    def run(self, input, params):
        pass


class Parser(EqualByNameMixIn):
    def __init__(self, name: str, params: Optional[dict] = None) -> None:
        self.name = name
        self.params = params
