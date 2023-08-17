from omymodels.types import (
    big_integer_types,
    boolean_types,
    datetime_types,
    float_types,
    integer_types,
    json_types,
    numeric_types,
    populate_types_mapping,
    string_types,
)

postgresql_dialect = ["ARRAY", "JSON", "JSONB", "UUID"]

mapper = {
    string_types: "sa.String",
    integer_types: "sa.Integer",
    big_integer_types: "sa.BigInteger",
    float_types: "sa.Float",
    numeric_types: "sa.Numeric",
    boolean_types: "sa.Boolean",
    datetime_types: "sa.DateTime",
    json_types: "JSON",
}

types_mapping = populate_types_mapping(mapper)

direct_types = {
    "date": "sa.Date",
    "timestamp": "sa.TIMESTAMP",
    "text": "sa.Text",
    "smallint": "sa.SmallInteger",
    "jsonb": "JSONB",
    "uuid": "UUID",
    "real": "sa.REAL",
}

types_mapping.update(direct_types)
