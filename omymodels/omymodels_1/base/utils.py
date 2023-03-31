from pydantic import BaseModel


class PydanticModel(BaseModel):

    class Config:
        arbitrary_types_allowed = True