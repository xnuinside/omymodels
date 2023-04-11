from ....base import BaseGenerator
from table_meta import TableMeta


class OMyModelsGenerator(BaseGenerator):
    """ default built in library models parser """
    name: str = 'omymodels'

    def run(self, input: TableMeta, params: dict):
        GeneratorConfig(**params)

