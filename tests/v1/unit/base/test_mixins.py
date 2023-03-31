from omymodels.omymodels_1.base.parser import Parser
from omymodels.omymodels_1.base.generator import Generator


def test_mixin_false_eq():
    assert Parser(name='omymodels') != Generator(name='omymodels')


def test_mixin_true_eq():
    assert Parser(name='omymodels') == Parser(name='omymodels') 
