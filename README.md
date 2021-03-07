## Status

    Work on first release in progress.

## O! My Models

O! My Models (omymodels) is a library to generate from SQL DDL Python Models for GinoORM (I hope to add several more ORMs in future).

You provide an input like:

```sql

    CREATE TABLE "materials" (
    "id" int PRIMARY KEY,
    "title" varchar NOT NULL default "New title",
    "description" varchar,
    "link" varchar,
    "created_at" timestamp,
    "updated_at" timestamp
    );

```

and got output:

```python




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

To parse DDL used small library - https://github.com/xnuinside/simple-ddl-parser.


## How to contribute

Please describe issue that you want to solve and open the PR, I will review it as soon as possible.

Any questions? Ping me in Telegram: https://t.me/xnuinside 