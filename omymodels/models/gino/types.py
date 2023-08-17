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

mapper = {
    string_types: "db.String",
    integer_types: "db.Integer",
    big_integer_types: "db.BigInteger",
    float_types: "db.Float",
    numeric_types: "db.Numeric",
    boolean_types: "db.Boolean",
    datetime_types: "db.DateTime",
    json_types: "JSON",
}

types_mapping = populate_types_mapping(mapper)

direct_types = {
    "date": "db.Date",
    "timestamp": "db.TIMESTAMP",
    "text": "db.Text",
    "smallint": "db.SmallInteger",
    "jsonb": "JSONB",
    "uuid": "UUID",
}


types_mapping.update(direct_types)
