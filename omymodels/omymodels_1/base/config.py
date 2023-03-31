from pydantic import root_validator, Field
from pathlib import Path
from .generator import Generator
from .parser import Parser
from typing import Union, Optional
from .utils import PydanticModel


class Config(PydanticModel):
    
    ddl_path: Path
    dump: bool
    dump_path: Path
    models_type: str = Field(default='pydantic')
    generator: Union[str, Generator] = Field(default='omymodels')
    parser: Union[str, Parser] = Field(default='omymodels')
    generator_params: Optional[dict]
    parser_params: Optional[dict]


    @root_validator
    def validator(cls, values):
        str_to_name_args = {
            'generator': Generator,
            'parser': Parser
        }
        for field_name, _class in str_to_name_args.items():
            values[field_name] = _class(
                name=values[field_name], 
                params=values.get(f'{field_name}_params')
            )
        return values
