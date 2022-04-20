from gino import Gino
from sqlalchemy.dialects.postgresql import ARRAY

db = Gino(schema="dbo")


class UsersWorkSchedule(db.Model):

    __tablename__ = 'users_WorkSchedule'

    id = db.Column(ARRAY((1,1)), primary_key=True)
    request_drop_date = db.Column(smalldatetime())
    shift_class = db.Column(db.String(5))
    start_history = db.Column(datetime2(7), nullable=False)
    end_history = db.Column(datetime2(7), nullable=False)
