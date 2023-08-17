import pytest

import omymodels
from omymodels import create_models


def test_no_tables():
    ddl = """
    CREATE schema aaa;
        """

    with pytest.raises(omymodels.errors.NoTablesError) as e:
        create_models(ddl=ddl)["code"]

    assert "No tables was found in DDL input" in str(e)


def test_no_tables_silent():
    ddl = """
    CREATE schema aaa;
        """

    with pytest.raises(SystemExit) as e:
        create_models(ddl=ddl, exit_silent=True)["code"]
        assert e.code == 0
