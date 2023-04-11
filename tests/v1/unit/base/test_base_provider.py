import pytest
from omymodels.omymodels_1.base import BaseGenerator, BaseParser


def test_name_type_validation():
    with pytest.raises(ValueError) as e:
        class CustomParser(BaseParser):

            @property
            def name(self):
                return 'custom-parser'

            def run(self):
                return "custom"

    assert 'name` variable of Provider class should have a string type' in str(e)


def test_name_exists():
    with pytest.raises(ValueError) as e:
        class CustomParser(BaseParser):

            def run(self):
                return "custom"

    assert 'You should define `name` class variable in your Provider class.' in str(e)
