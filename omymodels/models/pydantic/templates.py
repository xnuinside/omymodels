datetime_import = """import datetime"""
typing_imports = """from typing import {typing_types}"""
uuid_import = """from uuid import UUID"""

base_model = "BaseModel"

pydantic_imports = """from pydantic import {imports}"""

pydantic_class = """class {class_name}(BaseModel):"""
pydantic_attr = """    {arg_name}: {type}"""
pydantic_optional_attr = """    {arg_name}: Optional[{type}]"""
pydantic_default_attr = """ = {default}"""

enum_class = """class {class_name}({sub_type}):"""
enum_value = """    {name} = {value}"""
enum_import = "from enum import {enums}"

uuid_import = "from uuid import UUID"
