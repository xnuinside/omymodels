from abc import ABC, abstractmethod
from .mixins import EqualByNameMixIn


class BaseProvider(ABC, EqualByNameMixIn):

    name = 'base-provider'

    def __init_subclass__(cls, /, **kwargs):
        if not isinstance(cls.name, str):
            raise ValueError("`name`should be a class variable of type string")
        if cls.name == cls.mro()[1].name and cls.__name__ != cls.mro()[1].__name__:
            raise ValueError("You should define `name` class variable in your Provider class. "
                             "Name should be user friendly and will be used to choose provider with config")
        super().__init_subclass__(**kwargs)

    @abstractmethod
    def run(self, input, params):
        raise NotImplementedError(
            'Each Provider - Parser, Generator or Converter should have '
            '`run` method that takes some input and params to run with.'
        )
