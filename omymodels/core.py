from simple_ddl_parser import DDLParser, parse_from_file
from typing import Optional, List, Dict


def get_tables_information(ddl: Optional[str] =  None, ddl_file: Optional[str] = None):
    if not ddl_file and not ddl:
        raise ValueError(
            "You need to provide one of above argument: ddl with string that " \
            "contains ddl or ddl_file that contains path to ddl file to parse")
    if ddl:
        tables = DDLParser(ddl).run()
    elif ddl_file:
        tables = parse_from_file(ddl_file)


def generate_gino_models(tables: List[Dict]) -> str:
    pass


def save_models_to_file(models: str, dump_path: str) -> None:
    with open(dump_path, 'w+') as f:
        f.write(models)


def create_gino_models(ddl: Optional[str] = None, 
                               ddl_file: Optional[str] = None,
                               dump: bool = True,
                               dump_path: str = 'models.py'):
    tables = get_tables_information(ddl, ddl_file)
    models = generate_gino_models(tables)
    print(models)
    if dump:
        save_models_to_file(models, dump_path)
    else:
        print(models)
    


ddl = """
CREATE TABLE "materials" (
  "id" int PRIMARY KEY,
  "title" varchar NOT NULL default "New title",
  "description" varchar,
  "link" varchar,
  "created_at" timestamp,
  "updated_at" timestamp
);
"""

print(create_gino_model_from_ddl(ddl))

