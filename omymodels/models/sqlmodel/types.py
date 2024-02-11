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
    string_types: {"pydantic": "str", "sa": None},
    integer_types: {"pydantic": "int", "sa": None},
    big_integer_types: {"pydantic": "int", "sa": "sa.BigInteger"},
    float_types: {"pydantic": "float", "sa": None},
    numeric_types: {"pydantic": "decimal.Decimal", "sa": "sa.Numeric"},
    boolean_types: {"pydantic": "bool", "sa": None},
    datetime_types: {"pydantic": "datetime.datetime", "sa": None},
    json_types: {"pydantic": "Json", "sa": "JSON"},
}

types_mapping = populate_types_mapping(mapper)

direct_types = {
    "date": {"pydantic": "datetime.date", "sa": None},
    "timestamp": {"pydantic": "datetime.datetime", "sa": None},
    "time": {"pydantic": "datetime.time", "sa": "sa.Time"},
    "text": {"pydantic": "str", "sa": "sa.Text"},
    "longtext": {"pydantic": "str", "sa": "sa.Text"},  # confirm this is proper SA type.
    "mediumtext": {
        "pydantic": "str",
        "sa": "sa.Text",
    },  # confirm this is proper SA type.
    "tinytext": {"pydantic": "str", "sa": "sa.Text"},  # confirm this is proper SA type.
    "smallint": {"pydantic": "int", "sa": "sa.SmallInteger"},
    "jsonb": {"pydantic": "Json", "sa": "JSONB"},
    "uuid": {"pydantic": "UUID4", "sa": "UUID"},
    "real": {"pydantic": "float", "sa": "sa.REAL"},
    "int unsigned": {
        "pydantic": "int",
        "sa": None,
    },  # use mysql INTEGER(unsigned=True) for sa?
    "tinyint": {"pydantic": "int", "sa": None},  # what's the proper type for this?
    "tinyint unsigned": {
        "pydantic": "int",
        "sa": None,
    },  # what's the proper type for this?
    "smallint unsigned": {
        "pydantic": "int",
        "sa": None,
    },  # what's the proper type for this?
    "bigint unsigned": {"pydantic": "int", "sa": "sa.BigInteger"},
    # see https://sqlmodel.tiangolo.com/advanced/decimal/#decimals-in-sqlmodel
    "decimal unsigned": {"pydantic": "decimal.Decimal", "sa": None},
    "decimalunsigned": {"pydantic": "decimal.Decimal", "sa": None},
    # Points need extensions:
    #  geojson_pydantic and this import: from geojson_pydantic.geometries import Point
    #  geoalchemy2 and this import: from geoalchemy2 import Geometry
    # NOTE: SRID is not parsed currently.  Default values likely not correct.
    "point": {"pydantic": "Point", "sa": "Geography(geometry_type='POINT')"},
    "blob": {"pydantic": "bytes", "sa": "sa.LargeBinary"},
}

types_mapping.update(direct_types)
