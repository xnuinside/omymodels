from pydantic import BaseModel


class GeneratorConfig(BaseModel):

    schema_global: bool
    defaults_off: bool
