"""Example: Creating a custom generator for Peewee ORM.

This example shows how to add support for your own model type
without forking the repository.
"""

from omymodels import (
    BaseGenerator,
    TypeConverter,
    create_models,
    register_generator,
)

# Step 1: Define type mapping for your target framework
PEEWEE_TYPES = {
    "varchar": "CharField",
    "character varying": "CharField",
    "char": "FixedCharField",
    "text": "TextField",
    "integer": "IntegerField",
    "int": "IntegerField",
    "smallint": "SmallIntegerField",
    "bigint": "BigIntegerField",
    "serial": "AutoField",
    "bigserial": "BigAutoField",
    "boolean": "BooleanField",
    "bool": "BooleanField",
    "float": "FloatField",
    "double": "DoubleField",
    "decimal": "DecimalField",
    "numeric": "DecimalField",
    "date": "DateField",
    "time": "TimeField",
    "timestamp": "DateTimeField",
    "datetime": "DateTimeField",
    "uuid": "UUIDField",
    "json": "JSONField",
    "jsonb": "JSONField",
    "blob": "BlobField",
    "binary": "BlobField",
}


# Step 2: Create your generator class
class PeeweeGenerator(BaseGenerator):
    """Custom generator for Peewee ORM models."""

    def __init__(self):
        super().__init__()
        self.type_converter = TypeConverter(PEEWEE_TYPES)
        self.used_fields = set()

    def generate_model(self, table, singular=True, exceptions=None, **kwargs):
        """Generate a Peewee model class."""
        # Convert table name to class name
        class_name = self._to_class_name(table.name, singular)

        lines = [f"\nclass {class_name}(Model):"]
        lines.append(f'    """Model for {table.name} table."""')
        lines.append("")

        # Generate fields
        for column in table.columns:
            field_def = self._generate_field(column)
            lines.append(f"    {field_def}")

        # Add Meta class
        lines.append("")
        lines.append("    class Meta:")
        lines.append(f"        table_name = '{table.name}'")

        return "\n".join(lines)

    def create_header(self, tables, **kwargs):
        """Generate imports for Peewee."""
        # Collect all used field types
        all_fields = {"Model"}
        for table in tables:
            for column in table.columns:
                field_type = self.type_converter.convert(column.type)
                all_fields.add(field_type)

        fields_str = ", ".join(sorted(all_fields))
        return f"from peewee import {fields_str}\n"

    def _to_class_name(self, name, singular):
        """Convert table name to PascalCase class name."""
        # Remove quotes and schema prefix
        name = name.replace('"', "").replace("'", "")
        if "." in name:
            name = name.split(".")[-1]

        # Convert to PascalCase
        words = name.replace("-", "_").split("_")
        return "".join(word.capitalize() for word in words)

    def _generate_field(self, column):
        """Generate a single field definition."""
        field_type = self.type_converter.convert(column.type)
        self.used_fields.add(field_type)

        # Build field arguments
        args = []

        # Handle size for CharField
        if field_type == "CharField" and column.size:
            args.append(f"max_length={column.size}")

        # Handle nullable
        if column.nullable:
            args.append("null=True")

        # Handle primary key
        if column.primary_key:
            args.append("primary_key=True")

        # Handle default
        if column.default is not None:
            default = self._format_default(column.default)
            if default:
                args.append(f"default={default}")

        args_str = ", ".join(args)
        return f"{column.name} = {field_type}({args_str})"

    def _format_default(self, default):
        """Format default value for Python."""
        if default is None:
            return None

        default_str = str(default).strip()

        # Handle SQL NULL
        if default_str.upper() == "NULL":
            return "None"

        # Handle SQL functions
        if "now()" in default_str.lower() or "current_timestamp" in default_str.lower():
            return "datetime.datetime.now"

        # Handle boolean
        if default_str.upper() in ("TRUE", "FALSE"):
            return default_str.capitalize()

        # Handle numbers
        if default_str.replace(".", "").replace("-", "").isdigit():
            return default_str

        # Handle strings (add quotes if needed)
        if not default_str.startswith("'"):
            return f"'{default_str}'"

        return default_str


# Step 3: Register your generator
register_generator("peewee", PeeweeGenerator)


# Step 4: Use it!
if __name__ == "__main__":
    ddl = """
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) NOT NULL,
        email VARCHAR(255),
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT NOW()
    );

    CREATE TABLE posts (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        title VARCHAR(200) NOT NULL,
        content TEXT,
        published_at TIMESTAMP
    );
    """

    # Generate Peewee models
    result = create_models(ddl, models_type="peewee")
    print(result["code"])

    # Expected output:
    # from peewee import AutoField, BooleanField, CharField, DateTimeField, IntegerField, Model, TextField
    #
    # class User(Model):
    #     """Model for users table."""
    #
    #     id = AutoField(primary_key=True)
    #     username = CharField(max_length=100)
    #     email = CharField(max_length=255, null=True)
    #     is_active = BooleanField(default=True)
    #     created_at = DateTimeField(null=True, default=datetime.datetime.now)
    #
    #     class Meta:
    #         table_name = 'users'
    #
    # class Post(Model):
    #     """Model for posts table."""
    #
    #     id = AutoField(primary_key=True)
    #     user_id = IntegerField()
    #     title = CharField(max_length=200)
    #     content = TextField(null=True)
    #     published_at = DateTimeField(null=True)
    #
    #     class Meta:
    #         table_name = 'posts'
