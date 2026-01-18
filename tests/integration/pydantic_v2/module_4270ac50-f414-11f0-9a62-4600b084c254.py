from pydantic import BaseModel


class Config(BaseModel):

    id: int
    settings: dict | list
    metadata: dict | list | None = None
