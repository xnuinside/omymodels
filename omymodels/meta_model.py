from pydantic import BaseModel, Field, validator
from typing import List, Optional, Union


class TableProperties(BaseModel):

    indexes: List


class Column(BaseModel):

    name: str
    type: str
    size: Optional[Union[str, int, tuple]]
    primary_key: bool = False
    unique: bool = False
    default: Optional[str]
    nullable: bool = True
    identifier: Optional[bool]
    generated_as: Optional[str]
    other_properties: Optional[dict]
    references: Optional[dict]

    @validator("size")
    def size_must_contain_space(cls, v):
        if isinstance(v, str) and v.isnumeric():
            return int(v)
        return v


class TableMeta(BaseModel):
    name: str = Field(alias="table_name")
    table_schema: Optional[str] = Field(alias="schema")
    columns: List[Column]
    indexes: Optional[List[dict]] = Field(alias="index")
    alter: Optional[dict]
    checks: Optional[List[dict]]
    properties: Optional[TableProperties]
    primary_key: List

    class Config:
        """ pydantic class config """

        arbitrary_types_allowed = True


class Type(BaseModel):
    name: str = Field(alias="type_name")
    base_type: str
    properties: Optional[dict]
