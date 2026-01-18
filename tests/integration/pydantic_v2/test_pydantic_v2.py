import os
import sys

import pytest

from omymodels import create_models

# pydantic_v2 syntax (X | None) requires Python 3.10+ to work with Pydantic at runtime
pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="pydantic_v2 syntax requires Python 3.10+ for runtime evaluation"
)


def test_pydantic_v2_models_are_working_as_expected(load_generated_code) -> None:
    """Integration test: verify generated Pydantic v2 models are valid and usable."""
    ddl = """
    CREATE table user_history (
            runid                 decimal(21) null
        ,job_id                decimal(21)  null
        ,id                    varchar(100) not null
        ,user              varchar(100) not null
        ,status                varchar(10) not null
        ,event_time            timestamp not null default now()
        ,comment           varchar(1000) not null default 'none'
        ,event_time2           timestamp not null default current_timestamp
        ) ;


    """
    result = create_models(ddl, models_type="pydantic_v2")["code"]

    module = load_generated_code(result)

    # Create instance with required fields only
    used_model = module.UserHistory(
        id="group_id",
        user="user",
        status="active",
    )

    assert used_model
    assert used_model.id == "group_id"
    assert used_model.user == "user"
    assert used_model.status == "active"
    # nullable fields should default to None
    assert used_model.runid is None
    assert used_model.job_id is None

    os.remove(os.path.abspath(module.__file__))


def test_pydantic_v2_json_fields_work(load_generated_code) -> None:
    """Integration test: verify JSON fields work correctly in Pydantic v2."""
    ddl = """
    CREATE TABLE "config" (
        "id" SERIAL PRIMARY KEY,
        "settings" json NOT NULL,
        "metadata" jsonb
    );
    """
    result = create_models(ddl, models_type="pydantic_v2")["code"]

    module = load_generated_code(result)

    # Create instance with dict for JSON field
    config = module.Config(
        id=1,
        settings={"key": "value", "nested": {"a": 1}},
        metadata=None,
    )

    assert config
    assert config.settings == {"key": "value", "nested": {"a": 1}}
    assert config.metadata is None

    # Create instance with list for JSON field
    config2 = module.Config(
        id=2,
        settings=[1, 2, 3],
        metadata=["a", "b"],
    )

    assert config2.settings == [1, 2, 3]
    assert config2.metadata == ["a", "b"]

    os.remove(os.path.abspath(module.__file__))


def test_pydantic_v2_nullable_fields_work(load_generated_code) -> None:
    """Integration test: verify nullable fields with X | None syntax work."""
    ddl = """
    CREATE TABLE "person" (
        "name" varchar NOT NULL,
        "age" int NULL,
        "email" varchar NULL
    );
    """
    result = create_models(ddl, models_type="pydantic_v2")["code"]

    module = load_generated_code(result)

    # Create instance with optional fields as None
    person1 = module.Person(name="John")
    assert person1.name == "John"
    assert person1.age is None
    assert person1.email is None

    # Create instance with optional fields set
    person2 = module.Person(name="Jane", age=30, email="jane@example.com")
    assert person2.name == "Jane"
    assert person2.age == 30
    assert person2.email == "jane@example.com"

    os.remove(os.path.abspath(module.__file__))
