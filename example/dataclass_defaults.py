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
    link: str
    description: str = None
    type: MaterialType = None
    additional_properties: Union[dict, list] = None
    created_at: datetime.datetime = datetime.datetime.now()
    updated_at: datetime.datetime = None


@dataclass
class Author:
    id: int
    name: str = None
    link: str = None


@dataclass
class MaterialAuthors:
    category: int = None
    material: int = None


@dataclass
class MaterialPlatforms:
    category: int = None
    material: int = None


@dataclass
class Platform:
    id: int
    name: str
    link: str


@dataclass
class MaterialCategories:
    category: int = None
    material: int = None


@dataclass
class Category:
    id: int
    name: str
    description: str = None
    created_at: datetime.datetime = datetime.datetime.now()
    updated_at: datetime.datetime = None


@dataclass
class ContentFilters:
    category: int = None
    channels: List[str] = None
    words: List[str] = None
    created_at: datetime.datetime = datetime.datetime.now()
    updated_at: datetime.datetime = None
