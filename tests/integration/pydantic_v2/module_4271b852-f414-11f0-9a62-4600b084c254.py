from pydantic import BaseModel


class Person(BaseModel):

    name: str
    age: int | None = None
    email: str | None = None
