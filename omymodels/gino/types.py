postgresql_dialect = ["ARRAY", "JSON", "JSONB", "UUID"]

# key - type from ddl, value - type from GinoORM

types_mapping = {
    "varchar": "db.String",
    "float": "db.Float",
    "integer": "db.Integer",
    "date": "db.Date",
    "timestamp": "db.TIMESTAMP",
    "text": "db.Text",
    "smallint": "db.SmallInteger",
    "boolean": "db.Boolean",
    "bool": "db.Boolean",
    "decimal": "db.Numeric",
    "bigint": "db.BigInteger",
    "char": "db.String",
    "time": "db.DateTime",
    "numeric": "db.Numeric",
    "character": "db.String",
    "double": "db.Numeric",
    "character_vying": "db.String",
    "varying": "db.String",
    "serial": "db.Integer",
    "jsonb": "JSONB",
    "json": "JSON",
    "int": "db.Integer",
    "serial": "db.Integer",
    "bigserial": "db.BigInteger",
    "uuid": "UUID",
}


datetime_types = ["TIMESTAMP", "DATETIME", "DATE"]
