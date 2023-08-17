from gino import Gino

db = Gino()


class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    name = db.Column(db.String())
    created_at = db.Column(db.TIMESTAMP())
    updated_at = db.Column(db.TIMESTAMP())
    country_code = db.Column(db.Integer())
    default_language = db.Column(db.Integer())


class Languages(db.Model):
    __tablename__ = "languages"

    id = db.Column(db.Integer(), primary_key=True)
    code = db.Column(db.String(2), nullable=False)
    name = db.Column(db.String(), nullable=False)
