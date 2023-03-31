from omymodels.omymodels_1 import providers
from omymodels.omymodels_1.base import BaseGenerator, BaseParser
import pytest


def test_find_by_name_fail():
    with pytest.raises(ValueError) as e:
        providers.find_by_name('parser', 'test')
    assert 'does not exits in list of O!MyModels ' in str(e)


def test_add_provider_failed_not_class():
    with pytest.raises(ValueError) as e:
        providers.add_new(object())
    assert "Provider should be a class, not object or" in str(e)


def test_add_provider_failed():
    with pytest.raises(ValueError) as e:
        providers.add_new(object)
    assert "Provider should be created with inheritance from one of classes: "
    "omymodels.base.BaseParser or omymodels.base.BaseGenerator" in str(e)


def test_add_generator_success():
    class CustomGenerator(BaseGenerator):

        name: str = 'custom-generator'

        def run(self):
            return "custom"

    providers.add_new(CustomGenerator)
    assert CustomGenerator in providers.generators
    assert CustomGenerator not in providers.parsers


def test_add_parser_success():
    class CustomParser(BaseParser):

        name: str = 'custom-generator'

        def run(self):
            return "custom"

    providers.add_new(CustomParser)
    assert CustomParser in providers.parsers
    assert CustomParser not in providers.generators


def test_find_by_name():
    class CustomParser(BaseParser):
        name = 'custom-parser'

        def run(self):
            return "custom"

    providers.add_new(CustomParser)
    class CustomParser2(BaseParser):
        name = 'custom-parser2'

        def run(self):
            return "custom"

    providers.add_new(CustomParser2)
    assert providers.find_by_name('parser', 'custom-parser') == CustomParser
    assert CustomParser2 in providers.parsers

