import re

from typing import Optional, List, Text

from table_meta import Type


def from_class_to_table_name(name: str) -> str:
    return pluralize(name.lower())


def pluralize(word: str) -> str:

    no_plural = ["childrens"]
    if word in no_plural:
        return word

    if re.search("[sxz]$", word):
        word = re.sub("$", "es", word)
    elif re.search("[^aeioudgkprt]h$", word):
        word = re.sub("$", "es", word)
    elif re.search("[aeiou]y$", word):
        word = re.sub("y$", "ies", word)
    else:
        word = word + "s"

    return word


def get_singular_name(table_name: Text, exceptions: Optional[List] = None) -> Text:
    endings = {"ies": lambda x: x[:-3] + "y", "es": lambda x: x[:-1]}
    if not exceptions:
        exceptions = []
    exception_endings = [x for x in exceptions if table_name.endswith(x)]
    model_name = None
    if not exception_endings:
        for key in endings:
            if table_name.endswith(key):
                model_name = endings[key](table_name)
                break
    if not model_name:
        if table_name.endswith("s"):
            model_name = table_name[:-1]
        else:
            model_name = table_name
    return model_name


def create_class_name(
    table_name: Text, singular: bool = False, exceptions: Optional[List] = None
) -> Text:
    """ create correct class name for table in PascalCase """
    if singular:
        model_name = get_singular_name(table_name)
    else:
        model_name = table_name
    if "_" not in table_name or "-" not in table_name:
        if table_name.lower() != table_name and table_name.upper() != table_name:
            # mean already table in PascalCase
            return table_name
    model_name = model_name.replace("-", "_").replace("__", "_")
    model_name = model_name.capitalize()
    previous_symbol = None
    final_model_name = ""
    for symbol in model_name:
        if previous_symbol == "_":
            final_model_name = final_model_name[:-1]
            symbol = symbol.upper()
        previous_symbol = symbol
        final_model_name += symbol
    return final_model_name


enum_number_name_list = {
    0: "zero",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
}


def add_custom_types_to_generator(types: List[Type], generator: object) -> object:
    generator.custom_types = {
        _type.base_type.lower(): (f"{generator.prefix}Enum", _type.name)
        for _type in types
    }
    return generator
