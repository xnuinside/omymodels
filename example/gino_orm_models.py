from enum import Enum

from gino import Gino
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.sql import func

db = Gino()


class MaterialType(str, Enum):
    article = "article"
    video = "video"


class Material(db.Model):
    __tablename__ = "material"

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text())
    link = db.Column(db.String(), nullable=False)
    type = db.Column(db.Enum(MaterialType))
    additional_properties = db.Column(JSON())
    created_at = db.Column(db.TIMESTAMP(), server_default=func.now())
    updated_at = db.Column(db.TIMESTAMP())


class Author(db.Model):
    __tablename__ = "author"

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    name = db.Column(db.String())
    link = db.Column(db.String())


class MaterialAuthors(db.Model):
    __tablename__ = "material_authors"

    category = db.Column(db.Integer(), db.ForeignKey("author.id"))
    material = db.Column(db.Integer(), db.ForeignKey("material.id"))


class MaterialPlatforms(db.Model):
    __tablename__ = "material_platforms"

    category = db.Column(db.Integer(), db.ForeignKey("platform.id"))
    material = db.Column(db.Integer(), db.ForeignKey("material.id"))


class Platform(db.Model):
    __tablename__ = "platform"

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    link = db.Column(db.String(), nullable=False)


class MaterialCategories(db.Model):
    __tablename__ = "material_categories"

    category = db.Column(db.Integer(), db.ForeignKey("category.id"))
    material = db.Column(db.Integer(), db.ForeignKey("material.id"))


class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text())
    created_at = db.Column(db.TIMESTAMP(), server_default=func.now())
    updated_at = db.Column(db.TIMESTAMP())


class ContentFilters(db.Model):
    __tablename__ = "content_filters"

    category = db.Column(db.Integer(), db.ForeignKey("category.id"))
    channels = db.Column(ARRAY(db.String()))
    words = db.Column(ARRAY(db.String()))
    created_at = db.Column(db.TIMESTAMP(), server_default=func.now())
    updated_at = db.Column(db.TIMESTAMP())
