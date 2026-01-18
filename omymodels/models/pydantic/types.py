from omymodels.types import (
    big_integer_types,
    binary_types,
    boolean_types,
    datetime_types,
    float_types,
    integer_types,
    json_types,
    numeric_types,
    populate_types_mapping,
    string_types,
    text_types,
)

mapper = {
    string_types: "str",
    integer_types: "int",
    big_integer_types: "int",
    float_types: "float",
    numeric_types: "float",
    boolean_types: "bool",
    datetime_types: "datetime",
    json_types: "Any",
    text_types: "str",
    binary_types: "bytes",
}

types_mapping = populate_types_mapping(mapper)

direct_types = {
    "date": "date",
    "time": "time",
    "timestamp": "datetime",
    "smallint": "int",
    "json": "Any",
    "jsonb": "Any",
    "uuid": "UUID",
    "year": "int",
}

types_mapping.update(direct_types)
