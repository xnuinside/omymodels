## O! My Models

![badge1](https://img.shields.io/pypi/v/omymodels) ![badge2](https://img.shields.io/pypi/l/omymodels) ![badge3](https://img.shields.io/pypi/pyversions/omymodels)![workflow](https://github.com/xnuinside/omymodels/actions/workflows/main.yml/badge.svg)


## Try in Web-UI 
Try the online O!MyModels converter or simply use it online: https://archon-omymodels-online.hf.space/ (A big thanks for that goes to https://github.com/archongum)

## Examples 
You can find usage examples in the example/ folder on GitHub: https://github.com/xnuinside/omymodels/tree/main/example

## About library

O! My Models (omymodels) is a library that allow you to **generate** different ORM & pure Python models from SQL DDL or **convert** one models type to another (exclude SQLAlchemy Table, it does not supported yet by py-models-parser).

Supported Models:

- SQLAlchemy (https://docs.sqlalchemy.org/en/14/orm/), 
- SQLAlchemy Core (Tables) (https://docs.sqlalchemy.org/en/14/core/metadata.html#accessing-tables-and-columns),
- GinoORM (https://python-gino.org/), 
- Pydantic (https://pydantic-docs.helpmanual.io/),
- Python Enum (https://docs.python.org/3/library/enum.html) - generated only from DDL SQL Types,
- Python Dataclasses (dataclasses module) (https://docs.python.org/3/library/dataclasses.html),


## How to install

```bash

    pip install omymodels

```


## How to use

### From Python code
### Create Models from DDL

By default method **create_models** generate GinoORM models, to get Pydantic models output use the argument `models_type='pydantic'` ('sqlalchemy' for SQLAlchemy models; 'dataclass' for Dataclasses; 'sqlalchemy_core' for Sqlalchemy Core Tables).

A lot of examples in tests/ - https://github.com/xnuinside/omymodels/tree/main/tests.

For example,

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

 # and output will be:    
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

## TODO in next releases

1. Add Sequence generation in Models (Gino, SQLAlchemy)
2. Add support for pure Python Classes (https://docs.python.org/3/tutorial/classes.html#class-objects)
3. Add support for Tortoise ORM (https://tortoise-orm.readthedocs.io/en/latest/),
4. Add support for DjangoORM Models
5. Add support for Pydal Models
6. Add support for Encode/orm Models


## How to contribute
Please describe issue that you want to solve and open the PR, I will review it as soon as possible.

Any questions? Ping me in Telegram: https://t.me/xnuinside or mail xnuinside@gmail.com

If you see any bugs or have any suggestions - feel free to open the issue. Any help will be appritiated.

## Appretiation & thanks

One more time, big 'thank you!' goes to https://github.com/archongum for Web-version: https://archon-omymodels-online.hf.space/ 

## Changelog
**v0.17.0**

### Updates
1. fix character varying type - https://github.com/xnuinside/omymodels/issues/59
2. sqlalchemy import removed from generation in sqlmodels if it is not used
3.  = Field() - is not placed in SQLModel if there is no defaults or other settings to the field

**v0.16.0**

### Updates
1. Initial SQLModel Support


**v0.15.1**
## Updates
1. Foreign Key processing updates - https://github.com/xnuinside/omymodels/pull/55
2. Move to simple-ddl-parser version 1.X

**v0.14.0**
## Updates

1. Python 3.11 support. 


**v0.13.0**
## New feature

1. Added argument 'schema_global=' to support SQLAlchemy & Gino different table schemas https://github.com/xnuinside/omymodels/issues/41

**v0.12.1**
### Improvements

1. current_timestamp function processed now same was as "now()" function from ddl


**v0.12.0**
### Fixes
1. Now named arguments always went after positional. Fix for https://github.com/xnuinside/omymodels/issues/35

### New feature:
1. Availability to disable auto-name convertion - https://github.com/xnuinside/omymodels/issues/36. 
Now, if you want to keep names 1-to-1 as in your DDL file, you can set argument `no_auto_snake_case=True` and O!MyModels will do nothing with the table or column names.



**v0.11.1**

### Improvements:
1. added bytes type to pydantic - https://github.com/xnuinside/omymodels/pull/31
2. parser version updated to the latest 


**v0.11.0**

### Fixes:

1. MSSQL column & tables names in [] now is parsed validly  - https://github.com/xnuinside/omymodels/issues/28
2. names like 'users_WorkSchedule' now converted correctly to PascalCase like UsersWorkSchedule


**v0.10.1**
1. Update simple-ddl-parser version to 0.21.2


**v0.10.0**
### Improvements:
1. Meta models moved to separate package - https://github.com/xnuinside/table-meta
2. `common` module renamed to `from_ddl`, but anyway please use public API as imports from main module:

`from omymodels import create_models` or `from omymodels import convert_models`

### Fixes:

1. Fixed bunch of bugs in converter, but it stil in 'beta'.
2. Previously you can generate models if was any tables in ddl. Now you can also generate Enum models if in ddl you have only CREATE TYPE statements.
3. String enums now in any models types will be inherit from (str, Enum)


### Features:

1. Added converter feature to convert one model type to another (excluding SQLAlchemy Core (Tables)). 
Now with more tests for supported models, but still in Beta with bucnh of issues.

**v0.9.0**
Features:
1. Added beta models converter from one type of models to another.
To use models convertor:

```python
from omymodels import convert_models


models_from = """

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

"""

result = convert_models(models_from, models_type="gino")
print(result)
```

where `models_type` - type of models that you want to get as a result

2. Now if O!MyModels does not know how to convert type - he just leave it as is.

Fixes:
1. In Dataclass & Pydantic generators now Decimals & Floats converted to float (previously was int).

**v0.8.4**
1. Now if tables was not found in input DDL - models generator raise NoTable error. if you want to have still silent exit if no tables, please use flag: exit_silent

**v0.8.3**
1. Added fundamental concept of TableMetaModel - class that unifies metadata parsed from different classes/ORM models types/DDLs to one standard to allow easy way convert one models to another
in next releases it will be used for converter from one type of models to another.
2. Fixed issue: https://github.com/xnuinside/omymodels/issues/18 "NOW() not recognized as now()"
3. Fixed issue: https://github.com/xnuinside/omymodels/issues/19 "Default value of now() always returns same time, use field for dataclass"

**v0.8.1**
1. Parser version is updated (fixed several issues with generation)
2. Fixed issue with Unique Constraint after schema in SQLAlchemy Core

**v0.8.0**
1. Fix --defaults-off flag in cli
2. Added support for SQLAlchemy Core Tables generating
3. Added examples folder in github `omymodels/example`
4. Fix issue with ForeignKey in SQLAlchemy

**v0.7.0**
1. Added generation for SQLAlchemy models (defaults from DDLs are setting up as 'server_default')
2. Added defaults for Pydantic models
3. Added flag to generate Pydantic & Dataclass models WITHOUT defaults `defaults_off=True` (by default it is False). And cli flag --defaults-off
4. Fixed issue with Enum types with lower case names in DDLs
5. Fixed several issues with Dataclass generation (default with datetime & Enums)
6. '"' do not remove from defaults now

**v0.6.0**
1. O!MyModels now also can generate python Dataclass from DDL. Use argument models_type='dataclass' or if you use the cli flag --models_type dataclass or -m dataclass
2. Added ForeignKey generation to GinoORM Models, added support for ondelete and onupdate

**v0.5.0**
1. Added Enums/IntEnums types for Gino & Pydantic
2. Added UUID type
3. Added key `schema_global` in create_models method (by default schema_global = True). 
If you set schema_global=False schema if it exists in ddl will be defined for each table (model) in table args.
This way you can have differen schemas per model (table). By default schema_global=True - this mean for all 
table only one schema and it is defined in `db = Gino(schema="prefix--schema-name")`.
4. If column is a primary key (primary_key=True) nullable argument not showed, because primary keys always are not null.
5. To cli was added flag '--no-global-schema' to set schema in table_args.

**v0.4.1**
1. Added correct work with table names contains multiple '-'

**v0.4.0**
1. Added generation for Pydantic models from ddl
2. Main method create_gino_models renamed to create_models

**v0.3.0**
1. Generated Index for 'index' statement in __table_args__ (not unique constrait as previously)
2. Fix issue with column size as tuple (4,2)

**v0.2.0**
1. Valid generating columns in models: autoincrement, default, type, arrays, unique, primary key and etc.
2. Added creating __table_args__ for indexes
