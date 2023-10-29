from neomodel import (
    StructuredNode,
    IntegerProperty,
    FloatProperty,
    StringProperty,
    UniqueIdProperty,
    DateTimeProperty,
    Relationship
)


class Post(StructuredNode):
    post_id = UniqueIdProperty()
    title = StringProperty(required=True)
    description = StringProperty(required=True)
    amount = IntegerProperty(required=True)
    price = FloatProperty(required=True)
    publication_date = DateTimeProperty(default_now=True)

    categories = Relationship("models.category.Category", "HAS")
    multimedia_items = Relationship("models.post_multimedia_item.PostMultimediaItem", "HAS")
    comments = Relationship("models.comment.Comment", "HAS")
    liking_customers = Relationship("models.users.Customer", "LIKES")
    store = Relationship("models.users.Store", "POSTED")
    sales = Relationship("models.sale.Sale", "SOLD")
