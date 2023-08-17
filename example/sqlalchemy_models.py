from enum import Enum

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class MaterialType(str, Enum):
    article = "article"
    video = "video"


class Material(Base):
    __tablename__ = "material"

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    title = sa.Column(sa.String(), nullable=False)
    description = sa.Column(sa.Text())
    link = sa.Column(sa.String(), nullable=False)
    type = sa.Column(sa.Enum(MaterialType))
    additional_properties = sa.Column(JSON())
    created_at = sa.Column(sa.TIMESTAMP(), server_default=func.now())
    updated_at = sa.Column(sa.TIMESTAMP())


class Author(Base):
    __tablename__ = "author"

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    name = sa.Column(sa.String())
    link = sa.Column(sa.String())


class MaterialAuthors(Base):
    __tablename__ = "material_authors"

    category = sa.Column(sa.Integer(), sa.ForeignKey("author.id"))
    material = sa.Column(sa.Integer(), sa.ForeignKey("material.id"))


class MaterialPlatforms(Base):
    __tablename__ = "material_platforms"

    category = sa.Column(sa.Integer(), sa.ForeignKey("platform.id"))
    material = sa.Column(sa.Integer(), sa.ForeignKey("material.id"))


class Platform(Base):
    __tablename__ = "platform"

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    name = sa.Column(sa.String(), nullable=False)
    link = sa.Column(sa.String(), nullable=False)


class MaterialCategories(Base):
    __tablename__ = "material_categories"

    category = sa.Column(sa.Integer(), sa.ForeignKey("category.id"))
    material = sa.Column(sa.Integer(), sa.ForeignKey("material.id"))


class Category(Base):
    __tablename__ = "category"

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    name = sa.Column(sa.String(), nullable=False)
    description = sa.Column(sa.Text())
    created_at = sa.Column(sa.TIMESTAMP(), server_default=func.now())
    updated_at = sa.Column(sa.TIMESTAMP())


class ContentFilters(Base):
    __tablename__ = "content_filters"

    category = sa.Column(sa.Integer(), sa.ForeignKey("category.id"))
    channels = sa.Column(ARRAY(sa.String()))
    words = sa.Column(ARRAY(sa.String()))
    created_at = sa.Column(sa.TIMESTAMP(), server_default=func.now())
    updated_at = sa.Column(sa.TIMESTAMP())
