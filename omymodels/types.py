from typing import Any, Dict

from table_meta.model import Column

# Define PostgreSQL-specific dialect types
postgresql_dialect = [
    "ARRAY",
    "JSON",
    "JSONB",
    "UUID",
    "TIMESTAMPTZ",
    "INTERVAL",
    "BYTEA",
    "SERIAL",
    "BIGSERIAL",
]

# Define MySQL-specific dialect types
mysql_dialect = ["ENUM", "SET", "JSON"]

string_types = (
    "char",
    "character",
    "varchar",
    "character varying",
    "varying character",
    "string",
    "str",
)

text_types = (
    "text",
    "tinytext",
    "mediumtext",
    "longtext",
)

binary_types = (
    "binary",
    "varbinary",
    "blob",
    "tinyblob",
    "mediumblob",
    "longblob",
)

integer_types = (
    "tinyint",
    "smallint",
    "mediumint",
    "int",
    "integer",
)

big_integer_types = ("bigint",)

float_types = (
    "float",
    "double",
    "real",
)

numeric_types = (
    "decimal",
    "numeric",
)

boolean_types = (
    "boolean",
    "bool",
    "bit",
)

datetime_types = (
    "date",
    "datetime",
    "timestamp",
    "time",
    "year",
)

json_types = ("json",)

uuid_types = ("uuid",)

# PostgreSQL-Specific Types
postgresql_specific_mapper = {
    "array": "List[Any]",  # PostgreSQL arrays can be mapped to Python lists
    "json": "Any",
    "jsonb": "Any",
    "timestamptz": "datetime",  # For PostgreSQL's timezone-aware timestamp
    "interval": "float",  # Intervals can be represented as floating-point seconds
    "bytea": "bytes",  # PostgreSQL binary data
    "serial": "int",  # PostgreSQL auto-incrementing serial type
    "bigserial": "float",  # PostgreSQL auto-incrementing bigserial type
}

# MySQL-Specific Types
mysql_specific_mapper = {
    "enum": "str",  # Alternatively, map to specific Enum classes
    "set": "List[str]",
    "json": "Any",
}

# General mapper for both MySQL and PostgreSQL
mapper = {
    string_types: "str",
    text_types: "str",
    integer_types: "int",
    big_integer_types: "float",
    float_types: "float",
    numeric_types: "float",
    boolean_types: "bool",
    datetime_types: "datetime",
    binary_types: "bytes",
    json_types: "Any",
    uuid_types: "str",  # Map to 'str' to be compatible with Pydantic and then validated as UUID
    ("point",): "List[float]",  # Representing point as [float, float]
    ("linestring",): "List[List[float]]",  # List of points
    ("polygon",): "List[List[List[float]]]",  # List of LineStrings
}


def populate_types_mapping(mapper_dict: Dict[tuple, str]) -> Dict[str, str]:
    """
    Populates a dictionary mapping each type to its corresponding Pydantic type.
    All type keys are converted to lowercase for case-insensitive matching.
    """
    types_mapping = {}
    for type_group, pydantic_type in mapper_dict.items():
        for type_ in type_group:
            types_mapping[type_.lower()] = pydantic_type
    return types_mapping


# Generate the general types_mapping using the mapper
types_mapping = populate_types_mapping(mapper)


def prepare_type(column_data: Column, models_types_mapping: Dict[str, str]) -> str:
    """
    Determines the Pydantic type for a given column, handling special cases.
    Specifically maps 'tinyint(1)' to 'bool' in MySQL.
    """
    column_data_type = column_data.type.lower().split("[")[0]

    # Special handling for MySQL tinyint(1) -> bool
    if column_data_type.startswith("tinyint"):
        size = column_data.size
        if size == 1:
            return "bool"
        else:
            column_data_type = "tinyint"

    # Get the Pydantic type from the mapping
    column_type = models_types_mapping.get(column_data_type)

    # Default to the column data type if not found in mapping
    if not column_type:
        column_type = column_data_type

    return column_type


def add_custom_type_orm(
    custom_types: Dict[str, Any], column_data_type: str, column_type: str
) -> str:
    """
    Adds custom type mappings from the ORM's custom_types dictionary.
    """
    if "." in column_data_type:
        column_data_type = column_data_type.split(".")[1]
    column_type = custom_types.get(column_data_type, column_type)

    if isinstance(column_type, tuple):
        column_data_type = column_type[1]
        column_type = column_type[0]
    if column_type is not None:
        column_type = f"{column_type}({column_data_type})"
    return column_type


def set_column_size(column_type: str, column_data: Column) -> str:
    """
    Appends the size or precision/scale to the column type if applicable.
    """
    size = column_data.size
    if isinstance(size, int):
        column_type += f"({size})"
    elif isinstance(size, tuple):
        column_type += f"({','.join([str(x) for x in size])})"
    return column_type


def add_size_to_orm_column(column_type: str, column_data: Column) -> str:
    """
    Adds size information to the column type if available.
    """
    if column_data.size:
        column_type = set_column_size(column_type, column_data)
    elif column_type != "UUID" and "(" not in column_type:
        column_type += "()"
    return column_type


def process_types_after_models_parser(column_data: Column) -> Column:
    """
    Processes the column type string to remove schema qualifiers and parameters.
    """
    type_str = column_data.type
    if "." in type_str:
        type_str = type_str.split(".")[1]
    if "(" in type_str:
        if "Enum" not in type_str:
            type_str = type_str.split("(")[0]
        else:
            type_str = type_str.split("Enum(")[1].replace(")", "")
    column_data.type = type_str.lower()
    return column_data


def prepare_column_data(column_data: Column) -> Column:
    """
    Prepares the column data by processing the type string.
    """
    if "." in column_data.type or "(" in column_data.type:
        column_data = process_types_after_models_parser(column_data)
    return column_data


def prepare_column_type_orm(obj: Any, column_data: Column) -> str:
    """
    Prepares the Pydantic type for a given column based on the ORM object and column data.
    Handles both MySQL and PostgreSQL dialects, including custom types and size specifications.
    """
    column_type = None
    column_data = prepare_column_data(column_data)

    # Determine dialect based on obj; assuming obj has a 'dialect' attribute
    dialect = getattr(
        obj, "dialect", "mysql"
    ).lower()  # default to MySQL if not specified

    # Handle custom types if any
    if hasattr(obj, "custom_types") and obj.custom_types:
        column_type = add_custom_type_orm(
            obj.custom_types, column_data.type, column_type
        )

    # Prepare general type
    if not column_type:
        column_type = prepare_type(column_data, types_mapping)

    # Apply dialect-specific mappings
    if dialect == "postgresql":
        if column_type.upper() in postgresql_dialect:
            obj.postgresql_dialect_cols.add(column_type.upper())
        # Apply PostgreSQL-specific mappings
        column_type = postgresql_specific_mapper.get(column_type.lower(), column_type)
    elif dialect == "mysql":
        if column_type.upper() in mysql_dialect:
            obj.mysql_dialect_cols.add(column_type.upper())
        # Apply MySQL-specific mappings
        column_type = mysql_specific_mapper.get(column_type.lower(), column_type)

    # Add size if applicable
    column_type = add_size_to_orm_column(column_type, column_data)

    # Handle array types
    if (
        "[" in column_data.type
        and dialect == "postgresql"
        and column_data.type not in json_types
    ):
        obj.postgresql_dialect_cols.add("ARRAY")
        column_type = f"List[{column_type}]"
    elif (
        "[" in column_data.type
        and dialect == "mysql"
        and column_data.type not in json_types
    ):
        # MySQL doesn't support native arrays, consider using List or JSON
        obj.mysql_dialect_cols.add("ARRAY")
        column_type = f"List[{column_type}]"

    return column_type
