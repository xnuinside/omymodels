## O! My Models

![badge1](https://img.shields.io/pypi/v/omymodels) ![badge2](https://img.shields.io/pypi/l/omymodels) ![badge3](https://img.shields.io/pypi/pyversions/omymodels) 


O! My Models (omymodels) is a library to generate from SQL DDL Python Models for GinoORM (I hope to add several more ORMs in future) and Pydantic.

By default method **create_models** generate GinoORM models, to ger Pydantic models output use argument `models_type='pydantic'`

For example,

```python
from omymodels import create_models


ddl = """
CREATE table user_history (
        runid                 decimal(21) not null
    ,job_id                decimal(21) not null
    ,id                    varchar(100) not null -- group_id or role_id
    ,user              varchar(100) not null
    ,status                varchar(10) not null
    ,event_time            timestamp not null default now()
    ,comment           varchar(1000) not null default 'none'
    ) ;
"""
result = create_models(ddl, models_type='pydantic')

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

### How to install


```bash

    pip install omymodels

```

### How to use

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

Small library is used for parse DDL- https://github.com/xnuinside/simple-ddl-parser.


### What to do if types not supported in O! My Models and you cannot wait until PR will be approved

First of all, to parse types correct from DDL to models - they must be in types mypping, for Gino it exitst in this file:

omymodels/gino/types.py  **types_mapping**

If you need to use fast type that not exist in mapping - just do a path before call code with types_mapping.update()

for example:

```python

    from omymodels.gino import types
    from omymodels import create_models

    types.types_mapping.update({'your_type_from_ddl': 'db.TypeInGino'})

    ddl = "YOUR DDL with your custom your_type_from_ddl"

    models = create_models(ddl)

    #### And similar for Pydantic types

    from omymodels.pydantic import types  types_mapping
    from omymodels import create_models

    types.types_mapping.update({'your_type_from_ddl': 'db.TypeInGino'})

    ddl = "YOUR DDL with your custom your_type_from_ddl"

    models = create_models(ddl, models_type='pydantic')
```

## TODO in next releases

1. Add generating Sqlalchemy models.

## How to contribute

Please describe issue that you want to solve and open the PR, I will review it as soon as possible.

Any questions? Ping me in Telegram: https://t.me/xnuinside 

## Changelog
**v0.3.0**
1. Generated Index for 'index' statement in __table_args__ (not unique constrait as previously)
2. Fix issue with column size as tuple (4,2)

**v0.2.0**
1. Valid generating columns in models: autoincrement, default, type, arrays, unique, primary key and etc.
2. Added creating __table_args__ for indexes
