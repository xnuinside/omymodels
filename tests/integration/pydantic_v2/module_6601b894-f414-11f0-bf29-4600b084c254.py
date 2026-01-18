from __future__ import annotations

from pydantic import BaseModel


class Person(BaseModel):

    name: str
    age: int | None = None
    email: str | None = None
