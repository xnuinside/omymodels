## O! My Models

![badge1](https://img.shields.io/pypi/v/omymodels) ![badge2](https://img.shields.io/pypi/l/omymodels) ![badge3](https://img.shields.io/pypi/pyversions/omymodels)![workflow](https://github.com/xnuinside/omymodels/actions/workflows/main.yml/badge.svg)


## Try in Web-UI 
Try the online O!MyModels converter or simply use it online: https://archon-omymodels-online.hf.space/ (A big thanks for that goes to https://github.com/archongum)

## Examples 
You can find usage examples in the example/ folder on GitHub: https://github.com/xnuinside/omymodels/tree/main/example

## About library

O! My Models (omymodels) is a library that allow you to **generate** different ORM & pure Python models from SQL DDL or **convert** one models type to another (exclude SQLAlchemy Table, it does not supported yet by py-models-parser).

Supported Models:

- SQLAlchemy ORM (https://docs.sqlalchemy.org/en/20/orm/)
- SQLAlchemy Core (Tables) (https://docs.sqlalchemy.org/en/20/core/metadata.html)
- SQLModel (https://sqlmodel.tiangolo.com/) - combines SQLAlchemy and Pydantic
- GinoORM (https://python-gino.org/)
- Pydantic v1/v2 (https://docs.pydantic.dev/)
- Python Dataclasses (https://docs.python.org/3/library/dataclasses.html)
- Python Enum (https://docs.python.org/3/library/enum.html) - generated from DDL SQL Types
- OpenAPI 3 (Swagger) schemas (https://swagger.io/specification/)


## How to install

```bash

    pip install omymodels

```


## How to use

### From Python code
### Create Models from DDL

By default method **create_models** generates GinoORM models. Use the argument `models_type` to specify output format:
- `'pydantic'` - Pydantic v1 models (uses `Optional[X]`)
- `'pydantic_v2'` - Pydantic v2 models (uses `X | None` syntax, `dict | list` for JSON)
- `'sqlalchemy'` - SQLAlchemy ORM models
- `'sqlalchemy_core'` - SQLAlchemy Core Tables
- `'dataclass'` - Python Dataclasses
- `'sqlmodel'` - SQLModel models
- `'openapi3'` - OpenAPI 3 (Swagger) schema definitions

A lot of examples in tests/ - https://github.com/xnuinside/omymodels/tree/main/tests.

#### Pydantic v1 example

```python
from omymodels import create_models


ddl = """
CREATE table user_history (
     runid                 decimal(21) null
    ,job_id                decimal(21)  null
    ,id                    varchar(100) not null
    ,user              varchar(100) not null
    ,status                varchar(10) not null
    ,event_time            timestamp not null default now()
    ,comment           varchar(1000) not null default 'none'
    ) ;
"""
result = create_models(ddl, models_type='pydantic')['code']

# output:
import datetime
from typing import Optional
from pydantic import BaseModel


class UserHistory(BaseModel):

    runid: Optional[int]
    job_id: Optional[int]
    id: str
    user: str
    status: str
    event_time: datetime.datetime
    comment: str
```

#### Pydantic v2 example

```python
from omymodels import create_models


ddl = """
CREATE table user_history (
     runid                 decimal(21) null
    ,job_id                decimal(21)  null
    ,id                    varchar(100) not null
    ,user              varchar(100) not null
    ,status                varchar(10) not null
    ,event_time            timestamp not null default now()
    ,comment           varchar(1000) not null default 'none'
    ) ;
"""
result = create_models(ddl, models_type='pydantic_v2')['code']

# output:
from __future__ import annotations

import datetime
from pydantic import BaseModel


class UserHistory(BaseModel):

    runid: float | None = None
    job_id: float | None = None
    id: str
    user: str
    status: str
    event_time: datetime.datetime = datetime.datetime.now()
    comment: str = 'none'
```

**Key differences in Pydantic v2 output:**
- Uses `X | None` instead of `Optional[X]`
- Uses `dict | list` for JSON/JSONB types instead of `Json`
- Includes `from __future__ import annotations` for Python 3.9 compatibility
- Nullable fields automatically get `= None` default

To generate Dataclasses from DDL use argument `models_type='dataclass'`

for example:

```python
    #  (same DDL as in Pydantic sample)
    result = create_models(ddl, schema_global=False, models_type='dataclass')['code']

    # and result will be: 
    import datetime
    from dataclasses import dataclass


    @dataclass
    class UserHistory:

        id: str
        user: str
        status: str
        runid: int = None
        job_id: int = None
        event_time: datetime.datetime = datetime.datetime.now()
        comment: str = 'none'
```


GinoORM example. If you provide an input like:

```sql

CREATE TABLE "users" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar,
  "created_at" timestamp,
  "updated_at" timestamp,
  "country_code" int,
  "default_language" int
);

CREATE TABLE "languages" (
  "id" int PRIMARY KEY,
  "code" varchar(2) NOT NULL,
  "name" varchar NOT NULL
);


```

and you will get output:

```python

    from gino import Gino


    db = Gino()


    class Users(db.Model):

        __tablename__ = 'users'

        id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
        name = db.Column(db.String())
        created_at = db.Column(db.TIMESTAMP())
        updated_at = db.Column(db.TIMESTAMP())
        country_code = db.Column(db.Integer())
        default_language = db.Column(db.Integer())


    class Languages(db.Model):

        __tablename__ = 'languages'

        id = db.Column(db.Integer(), primary_key=True)
        code = db.Column(db.String(2))
        name = db.Column(db.String())


```

#### From cli

```bash

    omm path/to/your.ddl

    # for example
    omm tests/test_two_tables.sql

```

You can define target path where to save models with **-t**, **--target** flag:

```bash

    # for example
    omm tests/test_two_tables.sql -t test_path/test_models.py

```

If you want generate the Pydantic or Dataclasses models - just use flag **-m** or **--models_type='pydantic'** / **--models_type='dataclass'**

```bash

    omm /path/to/your.ddl -m dataclass

    # or 
    omm /path/to/your.ddl --models_type pydantic

```

Small library is used for parse DDL- https://github.com/xnuinside/simple-ddl-parser.


### What to do if types not supported in O!MyModels and you cannot wait until PR will be approved

First of all, to parse types correct from DDL to models - they must be in types mypping, for Gino it exitst in this file:

omymodels/gino/types.py  **types_mapping**

If you need to use fast type that not exist in mapping - just do a path before call code with types_mapping.update()

for example:

```python

    from omymodels.models.gino import types
    from omymodels import create_models

    types.types_mapping.update({'your_type_from_ddl': 'db.TypeInGino'})

    ddl = "YOUR DDL with your custom your_type_from_ddl"

    models = create_models(ddl)

    #### And similar for Pydantic types

    from omymodels.models.pydantic import types  types_mapping
    from omymodels import create_models

    types.types_mapping.update({'your_type_from_ddl': 'db.TypeInGino'})

    ddl = "YOUR DDL with your custom your_type_from_ddl"

    models = create_models(ddl, models_type='pydantic')
```

### Schema defenition

There is 2 ways how to define schema in Models:

1) Globally in Gino() class and it will be like this:

```python

    from gino import Gino
    db = Gino(schema="schema_name")

```

And this is a default way for put schema during generation - it takes first schema in tables and use it. 

2) But if you work with tables in different schemas, you need to define schema in each model in table_args. O!MyModels can do this also. Just use flag `--no-global-schema` if you use cli or put argument 'schema_global=False' to create_models() function if you use library from code. Like this:

```python

    ddl = """
    CREATE TABLE "prefix--schema-name"."table" (
    _id uuid PRIMARY KEY,
    one_more_id int
    );
        create unique index table_pk on "prefix--schema-name"."table" (one_more_id) ;
        create index table_ix2 on "prefix--schema-name"."table" (_id) ;
    """
    result = create_models(ddl, schema_global=False)
```

And result will be this:

``` python

    from sqlalchemy.dialects.postgresql import UUID
    from sqlalchemy.schema import UniqueConstraint
    from sqlalchemy import Index
    from gino import Gino

    db = Gino()


    class Table(db.Model):

        __tablename__ = 'table'

        _id = db.Column(UUID, primary_key=True)
        one_more_id = db.Column(db.Integer())

        __table_args__ = (
                    
        UniqueConstraint(one_more_id, name='table_pk'),
        Index('table_ix2', _id),
        dict(schema="prefix--schema-name")
                )
```

## OpenAPI 3 (Swagger) Support

O!MyModels supports bidirectional conversion with OpenAPI 3 schemas.

### Generate OpenAPI 3 schema from DDL

```python
from omymodels import create_models

ddl = """
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP
);
"""

result = create_models(ddl, models_type="openapi3")
print(result["code"])

# Output:
# {
#   "components": {
#     "schemas": {
#       "Users": {
#         "type": "object",
#         "properties": {
#           "id": {"type": "integer"},
#           "username": {"type": "string", "maxLength": 100},
#           "email": {"type": "string", "maxLength": 255},
#           "is_active": {"type": "boolean", "default": true},
#           "created_at": {"type": "string", "format": "date-time"}
#         },
#         "required": ["id", "username"]
#       }
#     }
#   }
# }
```

### Convert OpenAPI 3 schema to Python models

```python
from omymodels import create_models_from_openapi3

schema = """
{
    "components": {
        "schemas": {
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "created_at": {"type": "string", "format": "date-time"}
                },
                "required": ["id", "name"]
            }
        }
    }
}
"""

# Convert to Pydantic v2
result = create_models_from_openapi3(schema, models_type="pydantic_v2")
print(result)

# Output:
# from __future__ import annotations
#
# import datetime
# from pydantic import BaseModel
#
#
# class User(BaseModel):
#
#     id: int
#     name: str
#     email: str | None = None
#     created_at: datetime.datetime | None = None
```

YAML schemas are also supported (requires `pyyaml`):
```bash
pip install pyyaml
```

## Custom Generators (Plugin System)

You can add support for your own model types without forking the repository.

### Creating a Custom Generator

```python
from omymodels import BaseGenerator, TypeConverter, register_generator, create_models

# Define type mapping
MY_TYPES = {
    "varchar": "String",
    "integer": "Integer",
    "boolean": "Boolean",
    "timestamp": "DateTime",
}

class MyGenerator(BaseGenerator):
    def __init__(self):
        super().__init__()
        self.type_converter = TypeConverter(MY_TYPES)

    def generate_model(self, table, singular=True, **kwargs):
        class_name = table.name.title().replace("_", "")
        lines = [f"class {class_name}(MyBaseModel):"]
        for column in table.columns:
            col_type = self.type_converter.convert(column.type)
            lines.append(f"    {column.name}: {col_type}")
        return "\n".join(lines)

    def create_header(self, tables, **kwargs):
        return "from my_framework import MyBaseModel\n"

# Register and use
register_generator("my_framework", MyGenerator)
result = create_models(ddl, models_type="my_framework")
```

### Extending Built-in Generators

```python
from omymodels import register_generator
from omymodels.models.pydantic_v2.core import ModelGenerator as PydanticV2Generator

class CustomPydanticGenerator(PydanticV2Generator):
    def create_header(self, *args, **kwargs):
        header = super().create_header(*args, **kwargs)
        return "from my_types import CustomType\n" + header

register_generator("my_pydantic", CustomPydanticGenerator)
```

See full examples in `example/custom_generator.py` and `example/extend_builtin_generator.py`.

## TODO in next releases

1. Add Sequence generation in Models (Gino, SQLAlchemy)
2. Add support for Tortoise ORM (https://tortoise-orm.readthedocs.io/en/latest/)
3. Add support for DjangoORM Models
4. Add support for PyDAL Models (https://py4web.com/_documentation/static/en/chapter-07.html)


## How to contribute
Please describe issue that you want to solve and open the PR, I will review it as soon as possible.

Any questions? Ping me in Telegram: https://t.me/xnuinside or mail xnuinside@gmail.com

If you see any bugs or have any suggestions - feel free to open the issue. Any help will be appritiated.

## Appretiation & thanks

One more time, big 'thank you!' goes to https://github.com/archongum for Web-version: https://archon-omymodels-online.hf.space/ 

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for full version history.

### v1.0.0 Highlights

**Breaking Changes:**
- Dropped support for Python 3.7 and 3.8
- Minimum required Python version is now 3.9

**New Features:**
- Pydantic v2 support with native syntax (`X | None`, `dict | list`)
- OpenAPI 3 (Swagger) schema generation and conversion
- Plugin system for custom generators
- SQLModel array type support
- MySQL blob types support

**Improvements:**
- Simplified datetime imports
- Better Pydantic field handling (aliases, reserved names, generated columns)
- Enum functional syntax generation

See [CHANGELOG.md](CHANGELOG.md) for complete details and previous versions.
