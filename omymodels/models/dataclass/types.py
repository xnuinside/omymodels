from omymodels.types import (
    big_integer_types,
    boolean_types,
    float_types,
    integer_types,
    numeric_types,
    populate_types_mapping,
    string_types,
)

mapper = {
    string_types: "str",
    integer_types: "int",
    big_integer_types: "int",
    float_types: "float",
    numeric_types: "float",
    boolean_types: "bool",
}

types_mapping = populate_types_mapping(mapper)

direct_types = {
    "date": "datetime.date",
    "timestamp": "datetime.datetime",
    "text": "str",
    "smallint": "int",
    "time": "datetime.datetime",
    "jsonb": "Union[dict, list]",
    "json": "Union[dict, list]",
    "uuid": "UUID",
}


types_mapping.update(direct_types)
