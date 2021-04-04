datetime_import = """import datetime"""
typing_imports = """from typing import {typing_types}"""

base_model = 'BaseModel'

pydantic_imports = """from pydantic import {imports}"""

pydantic_class = """class {class_name}(BaseModel):"""
pydantic_attr = """    {arg_name}: {type}"""
pydantic_optional_attr = """    {arg_name}: Optional[{type}]"""
