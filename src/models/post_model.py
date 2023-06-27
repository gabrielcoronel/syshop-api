from neomodel import (
    StructuredNode,
    IntegerProperty,
    FloatProperty,
    StringProperty,
    UniqueIdProperty,
    DateTimeProperty,
    Relationship
)
from models.post_multimedia_model import PostMultimediaModel
from models.category_model import CategoryModel
from models.comment_model import CommentModel


class PostModel(StructuredNode):
    post_id = UniqueIdProperty()
    title = StringProperty(required=True)
    description = StringProperty(required=True)
    amount = IntegerProperty(required=True)
    price = FloatProperty(required=True)
    publication_date = DateTimeProperty(default_now=True)

    categories = Relationship("CategoryModel", "IS_CATEGORY_OF")
    multimedia = Relationship("PostMultimediaModel", "HAS")
    comments = Relationship("CommentModel", "HAS")
