from simple_ddl_parser import DDLParser, parse_from_file
from typing import Optional, List, Dict
import omymodels.gino.templates as gt
from omymodels.gino.types import types_mapping, postgresql_dialect


state = set()
postgresql_dialect = set()


def get_tables_information(ddl: Optional[str] =  None, ddl_file: Optional[str] = None) -> List[Dict]:
    if not ddl_file and not ddl:
        raise ValueError(
            "You need to provide one of above argument: ddl with string that " \
            "contains ddl or ddl_file that contains path to ddl file to parse")
    if ddl:
        tables = DDLParser(ddl).run()
    elif ddl_file:
        tables = parse_from_file(ddl_file)
    return tables


def generate_column(column_data: Dict, table_pk: List) -> str:
    column_type = types_mapping.get(column_data['type'].lower(), 
                                                'UNMAPPED')
    if column_type in postgresql_dialect:
        postgresql_dialect.add(column_type)
    column = gt.column_template.format(
            column_name=column_data['name'], column_type=column_type)
    if column_data['size']:
        column += f"({column_data['size']})"
    else:
        column += f"()"
    if column_data['type'].lower() == 'serial':
        column += gt.autoincrement
    if column_data['nullable']:
        column += gt.required
    if column_data['default']:
        if column_data['default'] == 'now()':
            column_data['default'] = 'func.now()'
            state.add('func')
        elif isinstance(column['default'], str):
            column_data['default'] = f"\'{column_data['default']}\'"
        column += gt.default(default=column_data['default'])
    if column_data['name'] in table_pk: 
        column += gt.pk_template
    column += ')\n'
    return column


def generate_model(table: Dict) -> str:
    model = gt.model_template.format(
        model_name=table['table_name'].capitalize(), 
        table_name=table['table_name'])
    for column in table['columns']:
        model += generate_column(column, table['primary_key'])
    return model


def generate_gino_models(tables: List[Dict]) -> str:
    output = ""
    for table in tables:
        output += generate_model(table)
    header = ""
    if 'func' in state:
        header += gt.sql_alchemy_func_import
    if postgresql_dialect:
        header += ",".join(postgresql_dialect)
    header += gt.gino_import + "\n\n"
    if tables[0]['schema']:
        header += gt.gino_init_schema + "\n"
    else:
        header += gt.gino_init + "\n"
    output = header + output  
    return output


def save_models_to_file(models: str, dump_path: str) -> None:
    with open(dump_path, 'w+') as f:
        f.write(models)


def create_gino_models(ddl: Optional[str] = None, 
                               ddl_path: Optional[str] = None,
                               dump: bool = True,
                               dump_path: str = 'models.py'):
    tables = get_tables_information(ddl, ddl_path)
    output = generate_gino_models(tables)
    if dump:
        save_models_to_file(output, dump_path)
    else:
        print(output)
