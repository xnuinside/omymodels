from ....base import BaseGenerator
from .config import GeneratorConfig
from table_meta import TableMeta


class OMyModelsGenerator(BaseGenerator):
    """ default built in library models generator """
    name: str = 'omymodels'

    def run(self, input: TableMeta, params: dict):
        GeneratorConfig(**params)

