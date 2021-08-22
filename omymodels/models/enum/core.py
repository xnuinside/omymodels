import pathlib
from typing import List, Dict, Tuple
from omymodels.helpers import enum_number_name_list, create_class_name

from table_meta import Type

from jinja2 import Template

enum_import = "from enum import {enums}"


class ModelGenerator:
    def __init__(self, types: List[str]) -> str:

        self.types = types
        self.enum_imports = set()
        self.custom_types = []

    def prepare_values(self, values: List[str]) -> Tuple[Dict, str]:
        result_values = {}

        values.sort()

        for num, value in enumerate(values):

            _value = value.replace("'", "")

            if not _value.isnumeric():
                result_values[value.replace("'", "")] = value
                self.enum_imports.add("Enum")
                parents = "str, Enum"
            else:
                result_values[enum_number_name_list.get(num)] = value
                parents = "IntEnum"
                self.enum_imports.add(parents)

        return result_values, parents

    def add_imports(self, parents: str) -> None:
        if "str" in parents:
            self.enum_imports.add(parents.split("str, ")[1].strip())
        else:
            self.enum_imports.add(parents)

    def process_type(self, _type: Type) -> None:
        _type.base_type = _type.name
        _type.name = create_class_name(_type.name)
        if not _type.attrs:
            _type.properties["values"], parents = self.prepare_values(
                _type.properties["values"]
            )
            _type.parents = parents
        else:
            _type.properties["values"] = {
                attr["name"]: attr["default"].replace('"', "") for attr in _type.attrs
            }
            _type.parents = ", ".join(_type.parents)

        self.add_imports(_type.parents)
        self.custom_types.append(_type.dict())

    def generate_type(self, types: List[Type]) -> str:
        """ method to prepare one Model defention - name & tablename  & columns """
        template_file = pathlib.Path(__file__).parent / "template.jinja2"
        for _type in types:
            self.process_type(_type)

        with open(template_file) as t:
            template = t.read()
            template = Template(template)
            params = {"custom_types": self.custom_types}
            return template.render(**params)

    def create_types(self) -> str:
        types_str = self.generate_type(self.types)
        self.custom_types = {x.name: ("db.Enum", x.name) for x in self.types}
        return types_str

    def create_header(self) -> str:
        self.enum_imports = list(self.enum_imports)
        self.enum_imports.sort()
        return enum_import.format(enums=", ".join(self.enum_imports)) + "\n"
