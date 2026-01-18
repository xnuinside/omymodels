import os

import pytest

from omymodels import create_models


def test_pydantic_models_are_working_as_expected(load_generated_code) -> None:
    ddl = """
    CREATE table user_history (
            runid                 decimal(21) null
        ,job_id                decimal(21)  null
        ,id                    varchar(100) not null -- group_id or role_id
        ,user              varchar(100) not null
        ,status                varchar(10) not null
        ,event_time            timestamp not null default now()
        ,comment           varchar(1000) not null default 'none'
        ,event_time2           timestamp not null default current_timestamp
        ) ;


    """
    result = create_models(ddl, models_type="pydantic")["code"]

    module = load_generated_code(result)

    used_model = module.UserHistory(
        id="group_id",
        user="user",
        status="active",
    )

    assert used_model

    os.remove(os.path.abspath(module.__file__))


def test_pydantic_max_length_validation(load_generated_code) -> None:
    """Integration test: verify max_length constraint is enforced (issue #48)."""
    from pydantic import ValidationError

    ddl = """
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(10) NOT NULL,
        email VARCHAR(50)
    );
    """
    result = create_models(ddl, models_type="pydantic")["code"]

    module = load_generated_code(result)

    # Valid data within max_length
    user = module.Users(id=1, name="John", email="john@example.com")
    assert user.name == "John"
    assert user.email == "john@example.com"

    # Name exceeds max_length of 10
    with pytest.raises(ValidationError) as exc_info:
        module.Users(id=2, name="A" * 11, email="test@example.com")
    assert "name" in str(exc_info.value)

    # Email exceeds max_length of 50
    with pytest.raises(ValidationError) as exc_info:
        module.Users(id=3, name="Jane", email="a" * 51)
    assert "email" in str(exc_info.value)

    os.remove(os.path.abspath(module.__file__))
