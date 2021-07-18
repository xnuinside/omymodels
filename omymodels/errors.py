class OMyModelsError(Exception):
    pass


class NoTablesError(OMyModelsError):
    def __init__(self, *args, **kwargs):
        default_msg = "No tables was found in DDL input."
        if not args:
            args = (default_msg,)
        super().__init__(*args, **kwargs)
