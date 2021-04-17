datetime_import = """import datetime"""
typing_imports = """from typing import {typing_types}"""
uuid_import = """from uuid import UUID"""

base_model = "BaseModel"

pydantic_imports = """from dataclasses import dataclass"""

pydantic_class = """@dataclass
class {class_name}:"""
dataclass_attr = """    {arg_name}: {type}"""
dataclass_default_attr = """ = {default}"""

enum_class = """class {class_name}({sub_type}):"""
enum_value = """    {name} = {value}"""
enum_import = "from enum import {enums}"

uuid_import = "from uuid import UUID"
