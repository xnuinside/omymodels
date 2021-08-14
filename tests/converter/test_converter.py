from omymodels import convert_models


def test_convert_models():

    models_from = """

    class MaterialType(str, Enum):

        article = "article"
        video = "video"


    @dataclass
    class Material:

        id: int
        title: str
        description: str
        link: str
        type: MaterialType
        additional_properties: Union[dict, list]
        created_at: datetime.datetime
        updated_at: datetime.datetime

    """

    result = convert_models(models_from)
    expected = """from gino import Gino
from sqlalchemy.dialects.postgresql import JSON

db = Gino()


class Material(db.Model):

    __tablename__ = 'Material'

    id = db.Column(db.Integer())
    title = db.Column(db.String())
    description = db.Column(db.String())
    link = db.Column(db.String())
    type = db.Column(db.Enum(MaterialType))
    additional_properties = db.Column(JSON())
    created_at = db.Column(db.DateTime())
    updated_at = db.Column(db.DateTime())
"""
    assert result == expected
