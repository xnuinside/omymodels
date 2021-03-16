
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
 

O! My Models (omymodels) is a library to generate from SQL DDL Python Models for GinoORM (I hope to add several more ORMs in future).

You provide an input like:

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

Small library is used for parse DDL- https://github.com/xnuinside/simple-ddl-parser.

What to do if types not supported in O! My Models and you cannot wait until PR will be approved
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First of all, to parse types correct from DDL to models - they must be in types mypping, for Gino it exitst in this file:

omymodels/gino/types.py  **types_mapping**

If you need to use fast type that not exist in mapping - just do a path before call code with types_mapping.update()

for example:

.. code-block:: python


       from omymodels.gino import types  types_mapping
       from omymodels import create_gino_models

       types.types_mapping.update({'your_type_from_ddl': 'db.TypeInGino'})

       ddl = "YOUR DDL with your custom your_type_from_ddl"

       models = create_gino_models(ddl)

How to contribute
-----------------

Please describe issue that you want to solve and open the PR, I will review it as soon as possible.

Any questions? Ping me in Telegram: https://t.me/xnuinside 

Changelog
---------

**v0.2.0**


#. Valid generating columns in models: autoincrement, default, type, arrays, unique, primary key and etc.
#. Added creating **table_args** for indexes
