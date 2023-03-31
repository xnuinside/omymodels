from .mixins import EqualByNameMixIn
from typing import Optional, Dict


class BaseContract(EqualByNameMixIn):

    providers: Dict[str, object]

    def __init__(self, name: str, params: Optional[dict] = None) -> None:

        self.name = name
        self.params = params
        self.provider_class: BaseProvider = self.get_real_class()
    
    def get_real_class(self):
        provider_class = self.providers.get(self.name)
        
        return provider_class
        

    def run(self):
        return self.real_class.run(params=self.params)
