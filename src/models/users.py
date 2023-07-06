from neomodel import (
    StructuredNode,
    StringProperty,
    FloatProperty,
    UniqueIdProperty,
    Relationship
)


class BaseUser(StructuredNode):
    user_id = UniqueIdProperty()
    picture = StringProperty(required=True)

    account = Relationship("models.accounts.BaseAccount", "IDENTIFIES")
    sessions = Relationship("models.session.Session", "HOLDS")
    chats = Relationship("models.session.Chat", "COMMUNICATES")


class Customer(BaseUser):
    name = StringProperty(required=True)
    first_surname = StringProperty(required=True)
    second_surname = StringProperty(required=True)

    locations = Relationship("models.location.Location", "HAS")
    purchases = Relationship("models.sale.Sale", "BOUGHT")
    liked_posts = Relationship("models.post.Post", "LIKES")


class Store(BaseUser):
    name = StringProperty(required=True)
    description = StringProperty(required=True)
    location_name = StringProperty(required=False)
    location_longitude = FloatProperty(required=False)
    location_latitude = FloatProperty(required=False)

    multimedia = Relationship("models.store_multimedia_item.StoreMultimediaItem", "HAS")
    sales = Relationship("models.sale.Sale", "SOLD")
    posts = Relationship("models.post.Post", "POSTED")
