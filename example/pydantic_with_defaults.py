import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Json


class MaterialType(str, Enum):
    article = "article"
    video = "video"


class Material(BaseModel):
    id: int
    title: str
    description: Optional[str]
    link: str
    type: Optional[MaterialType]
    additional_properties: Optional[Json]
    created_at: Optional[datetime.datetime] = datetime.datetime.now()
    updated_at: Optional[datetime.datetime]


class Author(BaseModel):
    id: int
    name: Optional[str]
    link: Optional[str]


class MaterialAuthors(BaseModel):
    category: Optional[int]
    material: Optional[int]


class MaterialPlatforms(BaseModel):
    category: Optional[int]
    material: Optional[int]


class Platform(BaseModel):
    id: int
    name: str
    link: str


class MaterialCategories(BaseModel):
    category: Optional[int]
    material: Optional[int]


class Category(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: Optional[datetime.datetime] = datetime.datetime.now()
    updated_at: Optional[datetime.datetime]


class ContentFilters(BaseModel):
    category: Optional[int]
    channels: Optional[List[str]]
    words: Optional[List[str]]
    created_at: Optional[datetime.datetime] = datetime.datetime.now()
    updated_at: Optional[datetime.datetime]
