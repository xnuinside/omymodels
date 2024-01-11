from omymodels import create_models


def test_no_unexpected_logs(capsys):
    ddl = """
    CREATE EXTERNAL TABLE test (
    test STRING NULL COMMENT 'xxxx',
    )
    PARTITIONED BY (snapshot STRING, cluster STRING)
    """

    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""
    create_models(ddl)
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""


def test_mssql_brackets_removed():
    ddl = """CREATE TABLE [dbo].[users_WorkSchedule](
        [id] [int] IDENTITY(1,1) NOT NULL,
        [RequestDropDate] [smalldatetime] NULL,
        [ShiftClass] [varchar](5) NULL,
        [StartHistory] [datetime2](7) GENERATED ALWAYS AS ROW START NOT NULL,
        [EndHistory] [datetime2](7) GENERATED ALWAYS AS ROW END NOT NULL,
        CONSTRAINT [PK_users_WorkSchedule_id] PRIMARY KEY CLUSTERED
        (
            [id] ASC
        )
        WITH (
            PAD_INDEX = OFF,
            STATISTICS_NORECOMPUTE = OFF,
            IGNORE_DUP_KEY = OFF,
            ALLOW_ROW_LOCKS = ON,
            ALLOW_PAGE_LOCKS = ON
        )  ON [PRIMARY],
        PERIOD FOR SYSTEM_TIME ([StartHistory], [EndHistory])
    )
  """
    result = create_models(ddl)
    expected = """from gino import Gino

db = Gino(schema="dbo")


class UsersWorkSchedule(db.Model):

    __tablename__ = 'users_WorkSchedule'

    id = db.Column(db.Integer(), primary_key=True)
    request_drop_date = db.Column(smalldatetime())
    shift_class = db.Column(db.String(5))
    start_history = db.Column(datetime2(7), nullable=False)
    end_history = db.Column(datetime2(7), nullable=False)
"""
    assert expected == result["code"]
