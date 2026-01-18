# Required for X | None syntax in Python 3.9
future_annotations = """from __future__ import annotations"""

datetime_import = """import datetime"""
typing_imports = """from typing import {typing_types}"""
uuid_import = """from uuid import UUID"""

base_model = "BaseModel"

pydantic_imports = """from pydantic import {imports}"""

pydantic_class = """class {class_name}(BaseModel):"""
# Pydantic v2 style: use X | None instead of Optional[X]
pydantic_attr = """    {arg_name}: {type}"""
pydantic_nullable_attr = """    {arg_name}: {type} | None"""
pydantic_default_attr = """ = {default}"""

enum_class = """class {class_name}({sub_type}):"""
enum_value = """    {name} = {value}"""
enum_import = "from enum import {enums}"

uuid_import = "from uuid import UUID"
