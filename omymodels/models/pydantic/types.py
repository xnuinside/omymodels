from omymodels.types import mapper, populate_types_mapping

direct_types = {
    ("date",): "date",
    ("time",): "time",
    ("year",): "int",
}

types_mapping = populate_types_mapping({**mapper, **direct_types})
