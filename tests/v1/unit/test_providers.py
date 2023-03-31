from omymodels.omymodels_1.providers import providers
import pytest


def test_find_by_name_fail():
    with pytest.raises(ValueError) as e:
        providers.find_by_name('parsers', 'test')
    assert 'does not exits in list of O!MyModels ' in str(e)


def test_add_provider_failed():
    with pytest.raises(ValueError) as e:
        providers.add_new(object())
    assert "Provider should be created with inheritance from one of classes: "
    "omymodels.base.BaseParser or omymodels.base.BaseGenerator" in str(e)
