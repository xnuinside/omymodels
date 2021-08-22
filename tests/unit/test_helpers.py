from omymodels.helpers import from_class_to_table_name as fr


def test_from_class_to_table_name():
    assert fr("Model") == "models"
    assert fr("play") == "plaies"
    assert fr("Games") == "gameses"
