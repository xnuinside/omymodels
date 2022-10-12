import os

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
