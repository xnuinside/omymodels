"""SQL type definitions and groupings."""

# PostgreSQL dialect types that need special imports
postgresql_dialect = ["ARRAY", "JSON", "JSONB", "UUID"]

# String types
string_types = (
    "str",
    "varchar",
    "character",
    "character varying",
    "varying",
    "char",
    "string",
    "String",
)

text_types = ("text", "Text")

# Binary types
binary_types = (
    "BINARY",
    "VARBINARY",
    "binary",
    "varbinary",
    "tinyblob",
    "blob",
    "mediumblob",
    "longblob",
)

# JSON types
json_types = ("union[dict, list]", "json", "jsonb", "union")

# Integer types
integer_types = ("integer", "int", "serial", "smallint", "tinyint", "mediumint")

big_integer_types = ("bigint", "bigserial")

# Float types
float_types = ("float", "real")

numeric_types = ("decimal", "numeric", "double", "double precision", "money")

# Boolean types
boolean_types = ("boolean", "bool")

# Datetime types
datetime_types = (
    "TIMESTAMP",
    "DATETIME",
    "DATE",
    "TIME",
    "datetime.datetime",
    "datetime",
    "datetime.date",
    "date",
    "time",
)

# UUID type
uuid_types = ("uuid",)

# All type groups for iteration
ALL_TYPE_GROUPS = {
    "string": string_types,
    "text": text_types,
    "binary": binary_types,
    "json": json_types,
    "integer": integer_types,
    "big_integer": big_integer_types,
    "float": float_types,
    "numeric": numeric_types,
    "boolean": boolean_types,
    "datetime": datetime_types,
    "uuid": uuid_types,
}
