from omymodels.omymodels_1.base import BaseGenerator, BaseParser


def test_add_parser_success():
    class CustomParser(BaseParser):

        @property
        def name(self):
            return 'custom-parser'

        def run(self):
            return "custom"

    providers.add_new(CustomParser)