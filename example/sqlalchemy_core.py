from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY,JSON
import sqlalchemy as sa
from sqlalchemy import Table, Column, MetaData


metadata = MetaData()


class MaterialType(Enum):

    article = 'article'
    video = 'video'


material = Table("material", metadata,
        Column(sa.Integer(), autoincrement=True, primary_key=True),
        Column(sa.String(), nullable=False),
        Column(sa.Text()),
        Column(sa.String(), nullable=False),
        Column(sa.Enum(MaterialType)),
        Column(JSON()),
        Column(sa.TIMESTAMP(), server_default=func.now()),
        Column(sa.TIMESTAMP()),
)


author = Table("author", metadata,
        Column(sa.Integer(), autoincrement=True, primary_key=True),
        Column(sa.String()),
        Column(sa.String()),
)


material_authors = Table("material_authors", metadata,
        Column(sa.Integer(), sa.ForeignKey('author.id')),
        Column(sa.Integer(), sa.ForeignKey('material.id')),
)


material_platforms = Table("material_platforms", metadata,
        Column(sa.Integer(), sa.ForeignKey('platform.id')),
        Column(sa.Integer(), sa.ForeignKey('material.id')),
)


platform = Table("platform", metadata,
        Column(sa.Integer(), autoincrement=True, primary_key=True),
        Column(sa.String(), nullable=False),
        Column(sa.String(), nullable=False),
)


material_categories = Table("material_categories", metadata,
        Column(sa.Integer(), sa.ForeignKey('category.id')),
        Column(sa.Integer(), sa.ForeignKey('material.id')),
)


category = Table("category", metadata,
        Column(sa.Integer(), autoincrement=True, primary_key=True),
        Column(sa.String(), nullable=False),
        Column(sa.Text()),
        Column(sa.TIMESTAMP(), server_default=func.now()),
        Column(sa.TIMESTAMP()),
)


content_filters = Table("content_filters", metadata,
        Column(sa.Integer(), sa.ForeignKey('category.id')),
        Column(ARRAY(sa.String())),
        Column(ARRAY(sa.String())),
        Column(sa.TIMESTAMP(), server_default=func.now()),
        Column(sa.TIMESTAMP()),
)
