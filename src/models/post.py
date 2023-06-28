from neomodel import (
    StructuredNode,
    IntegerProperty,
    FloatProperty,
    StringProperty,
    UniqueIdProperty,
    DateTimeProperty,
    Relationship
)
from models.category import Category
from models.post_multimedia_item import PostMultimediaItem
from models.comment import Comment


class Post(StructuredNode):
    post_id = UniqueIdProperty()
    title = StringProperty(required=True)
    description = StringProperty(required=True)
    amount = IntegerProperty(required=True)
    price = FloatProperty(required=True)
    publication_date = DateTimeProperty(default_now=True)

    categories = Relationship("Category", "HAS")
    multimedia_items = Relationship("PostMultimediaItem", "HAS")
    comments = Relationship("Comment", "HAS")
