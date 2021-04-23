postgresql_dialect = ["ARRAY", "JSON", "JSONB", "UUID"]

# key - type from ddl, value - type from sqlalchemyORM

types_mapping = {
    "varchar": "sa.String",
    "float": "sa.Float",
    "integer": "sa.Integer",
    "date": "sa.Date",
    "timestamp": "sa.TIMESTAMP",
    "text": "sa.Text",
    "smallint": "sa.SmallInteger",
    "boolean": "sa.Boolean",
    "bool": "sa.Boolean",
    "decimal": "sa.Numeric",
    "bigint": "sa.BigInteger",
    "char": "sa.String",
    "time": "sa.DateTime",
    "numeric": "sa.Numeric",
    "character": "sa.String",
    "double": "sa.Numeric",
    "character_vying": "sa.String",
    "varying": "sa.String",
    "serial": "sa.Integer",
    "jsonb": "JSONB",
    "json": "JSON",
    "int": "sa.Integer",
    "serial": "sa.Integer",
    "bigserial": "sa.BigInteger",
    "uuid": "UUID",
}


datetime_types = ["TIMESTAMP", "DATETIME", "DATE"]
