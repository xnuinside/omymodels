from abc import ABC, abstractmethod, abstractproperty
from .mixins import EqualByNameMixIn


class BaseProvider(ABC, EqualByNameMixIn):

    @abstractproperty
    def name(self):
        raise NotImplementedError(
            'Each Provider - Parser, Generator or Converter should have name. '
            'This name used to identify it in the list of available providers for users')

    @abstractmethod
    def run(self, input, params):
        raise NotImplementedError(
            'Each Provider - Parser, Generator or Converter should have '
            '`run` method that takes some input and params to run with.'
        )
