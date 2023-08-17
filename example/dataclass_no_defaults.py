import datetime
from dataclasses import dataclass
from enum import Enum
from typing import List, Union


class MaterialType(str, Enum):
    article = "article"
    video = "video"


@dataclass
class Material:
    id: int
    title: str
    description: str
    link: str
    type: MaterialType
    additional_properties: Union[dict, list]
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class Author:
    id: int
    name: str
    link: str


@dataclass
class MaterialAuthors:
    category: int
    material: int


@dataclass
class MaterialPlatforms:
    category: int
    material: int


@dataclass
class Platform:
    id: int
    name: str
    link: str


@dataclass
class MaterialCategories:
    category: int
    material: int


@dataclass
class Category:
    id: int
    name: str
    description: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class ContentFilters:
    category: int
    channels: List[str]
    words: List[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime
