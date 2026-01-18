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

# SQLAlchemy 2.0 type mapping: {sql_type: {"python": python_type, "sa": sa_column_type}}
mapper = {
    string_types: {"python": "str", "sa": "String"},
    integer_types: {"python": "int", "sa": "Integer"},
    big_integer_types: {"python": "int", "sa": "BigInteger"},
    float_types: {"python": "float", "sa": "Float"},
    numeric_types: {"python": "float", "sa": "Numeric"},
    boolean_types: {"python": "bool", "sa": "Boolean"},
    datetime_types: {"python": "datetime", "sa": "DateTime"},
    json_types: {"python": "dict", "sa": "JSON"},
    text_types: {"python": "str", "sa": "Text"},
    binary_types: {"python": "bytes", "sa": "LargeBinary"},
}

types_mapping = populate_types_mapping(mapper)

direct_types = {
    "date": {"python": "date", "sa": "Date"},
    "time": {"python": "time", "sa": "Time"},
    "timestamp": {"python": "datetime", "sa": "DateTime"},
    "smallint": {"python": "int", "sa": "SmallInteger"},
    "uuid": {"python": "UUID", "sa": "UUID"},
    "json": {"python": "dict", "sa": "JSON"},
    "jsonb": {"python": "dict", "sa": "JSON"},
    "year": {"python": "int", "sa": "Integer"},
}

types_mapping.update(direct_types)

# Python type to SQLAlchemy type fallback for arrays
python_to_sa_type = {
    "int": "Integer",
    "str": "String",
    "float": "Float",
    "bool": "Boolean",
    "datetime": "DateTime",
    "date": "Date",
    "time": "Time",
    "bytes": "LargeBinary",
}
