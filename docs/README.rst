
O! My Models
------------


.. image:: https://img.shields.io/pypi/v/omymodels
   :target: https://img.shields.io/pypi/v/omymodels
   :alt: badge1
 
.. image:: https://img.shields.io/pypi/l/omymodels
   :target: https://img.shields.io/pypi/l/omymodels
   :alt: badge2
 
.. image:: https://img.shields.io/pypi/pyversions/omymodels
   :target: https://img.shields.io/pypi/pyversions/omymodels
   :alt: badge3

.. image:: https://github.com/xnuinside/omymodels/actions/workflows/main.yml/badge.svg
   :target: https://github.com/xnuinside/omymodels/actions/workflows/main.yml/badge.svg
   :alt: workflow


Big example you can find in example/ folder on the github: https://github.com/xnuinside/omymodels/tree/main/example

O! My Models (omymodels) is a library to generate from SQL DDL Python Models for SQLAlchemy (models), SQLAlchemy Core (tables), GinoORM (I hope to add several more ORMs in future), Pydantic classes and Python Dataclasses (dataclasses module).

By default method **create_models** generate GinoORM models, to get Pydantic models output use the argument ``models_type='pydantic'`` ('sqlalchemy' for SQLAlchemy models; 'dataclass' for Dataclasses; 'sqlalchemy_core' for Sqlalchemy Core Tables).

A lot of examples in tests/ - https://github.com/xnuinside/omymodels/tree/main/tests.

For example,

.. code-block:: python

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

To generate Dataclasses from DDL use argument ``models_type='dataclass'``

for example:

.. code-block:: python

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

GinoORM example. If you provide an input like:

.. code-block:: sql


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

and you will get output:

.. code-block:: python


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

How to install
^^^^^^^^^^^^^^

.. code-block:: bash


       pip install omymodels

How to use
^^^^^^^^^^

From cli
~~~~~~~~

.. code-block:: bash


       omm path/to/your.ddl

       # for example
       omm tests/test_two_tables.sql

You can define target path where to save models with **-t**\ , **--target** flag:

.. code-block:: bash


       # for example
       omm tests/test_two_tables.sql -t test_path/test_models.py

If you want generate the Pydantic or Dataclasses models - just use flag **-m** or **--models_type='pydantic'** / **--models_type='dataclass'**

.. code-block:: bash


       omm /path/to/your.ddl -m dataclass

       # or 
       omm /path/to/your.ddl --models_type pydantic

Small library is used for parse DDL- https://github.com/xnuinside/simple-ddl-parser.

What to do if types not supported in O! My Models and you cannot wait until PR will be approved
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First of all, to parse types correct from DDL to models - they must be in types mypping, for Gino it exitst in this file:

omymodels/gino/types.py  **types_mapping**

If you need to use fast type that not exist in mapping - just do a path before call code with types_mapping.update()

for example:

.. code-block:: python


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

Schema defenition
^^^^^^^^^^^^^^^^^

There is 2 ways how to define schema in Models:

1) Globally in Gino() class and it will be like this:

.. code-block:: python


       from gino import Gino
       db = Gino(schema="schema_name")

And this is a default way for put schema during generation - it takes first schema in tables and use it. 

2) But if you work with tables in different schemas, you need to define schema in each model in table_args. O!MyModels can do this also. Just use flag ``--no-global-schema`` if you use cli or put argument 'schema_global=False' to create_models() function if you use library from code. Like this:

.. code-block:: python


       ddl = """
       CREATE TABLE "prefix--schema-name"."table" (
       _id uuid PRIMARY KEY,
       one_more_id int
       );
           create unique index table_pk on "prefix--schema-name"."table" (one_more_id) ;
           create index table_ix2 on "prefix--schema-name"."table" (_id) ;
       """
       result = create_models(ddl, schema_global=False)

And result will be this:

.. code-block:: python


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

TODO in next releases
---------------------


#. Add Sequence generation in Models (Gino, SQLAlchemy)
#. Generate Tortoise ORM models (https://tortoise-orm.readthedocs.io/en/latest/)
#. Convert SQLAlchemy models to DjangoORM, Pydantic, SQLAlchemy Tables, Dataclasses (?)

How to contribute
-----------------

Please describe issue that you want to solve and open the PR, I will review it as soon as possible.

Any questions? Ping me in Telegram: https://t.me/xnuinside

Changelog
---------

**v0.8.3**


#. Added fundamental concept of TableMetaModel - class that unifies metadata parsed from different classes/ORM models types/DDLs to one standard to allow easy way convert one models to another
   in next releases it will be used for converter from one type of models to another.
#. Fixed issue: https://github.com/xnuinside/omymodels/issues/18 "NOW() not recognized as now()"
#. Fixed issue: https://github.com/xnuinside/omymodels/issues/19 "Default value of now() always returns same time, use field for dataclass"

**v0.8.1**


#. Parser version is updated (fixed several issues with generation)
#. Fixed issue with Unique Constraint after schema in SQLAlchemy Core

**v0.8.0**


#. Fix --defaults-off flag in cli
#. Added support for SQLAlchemy Core Tables generating
#. Added examples folder in github ``omymodels/example``
#. Fix issue with ForeignKey in SQLAlchemy

**v0.7.0**


#. Added generation for SQLAlchemy models (defaults from DDLs are setting up as 'server_default')
#. Added defaults for Pydantic models
#. Added flag to generate Pydantic & Dataclass models WITHOUT defaults ``defaults_off=True`` (by default it is False). And cli flag --defaults-off
#. Fixed issue with Enum types with lower case names in DDLs
#. Fixed several issues with Dataclass generation (default with datetime & Enums)
#. '"' do not remove from defaults now

**v0.6.0**


#. O!MyModels now also can generate python Dataclass from DDL. Use argument models_type='dataclass' or if you use the cli flag --models_type dataclass or -m dataclass
#. Added ForeignKey generation to GinoORM Models, added support for ondelete and onupdate

**v0.5.0**


#. Added Enums/IntEnums types for Gino & Pydantic
#. Added UUID type
#. Added key ``schema_global`` in create_models method (by default schema_global = True). 
   If you set schema_global=False schema if it exists in ddl will be defined for each table (model) in table args.
   This way you can have differen schemas per model (table). By default schema_global=True - this mean for all 
   table only one schema and it is defined in ``db = Gino(schema="prefix--schema-name")``.
#. If column is a primary key (primary_key=True) nullable argument not showed, because primary keys always are not null.
#. To cli was added flag '--no-global-schema' to set schema in table_args.

**v0.4.1**


#. Added correct work with table names contains multiple '-'

**v0.4.0**


#. Added generation for Pydantic models from ddl
#. Main method create_gino_models renamed to create_models

**v0.3.0**


#. Generated Index for 'index' statement in **table_args** (not unique constrait as previously)
#. Fix issue with column size as tuple (4,2)

**v0.2.0**


#. Valid generating columns in models: autoincrement, default, type, arrays, unique, primary key and etc.
#. Added creating **table_args** for indexes
