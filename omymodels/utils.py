from typing import Optional, List, Text

type_not_found = "OMM_UNMAPPED_TYPE"


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
