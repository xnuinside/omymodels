from omymodels.omymodels_1.base.config import Config
from omymodels.omymodels_1.base.generator import Generator
from omymodels.omymodels_1.base.parser import Parser


def test_config_generators():
    config = Config(
        generator='test-generator',
        ddl_path='./',
        dump=True,
        dump_path='./',
        parser='test-parser'
        )
    assert config.generator == Generator(name='test-generator')
    assert config.parser == Parser(name='test-parser')


def test_config_params_generator():

    config = Config(
        generator='test-generator',
        ddl_path='./',
        dump=True,
        dump_path='./',
        parser='test-parser',
        generator_params={'params': 'gen'},
        parser_params={'params': 'pars'}
        )
    assert config.generator.params == config.generator_params
    assert config.parser.params == config.parser_params