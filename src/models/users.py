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
    chats = Relationship("models.chat.Chat", "COMMUNICATES")


class Customer(BaseUser):
    name = StringProperty(required=True)
    first_surname = StringProperty(required=True)
    second_surname = StringProperty(required=True)

    locations = Relationship("models.location.Location", "HAS")
    purchases = Relationship("models.sale.Sale", "BOUGHT")
    liked_posts = Relationship("models.post.Post", "LIKES")
    following = Relationship("models.users.Store", "FOLLOWS")


class Store(BaseUser):
    name = StringProperty(required=True)
    description = StringProperty(required=True)

    multimedia = Relationship("models.store_multimedia_item.StoreMultimediaItem", "HAS")
    sales = Relationship("models.sale.Sale", "SOLD")
    posts = Relationship("models.post.Post", "POSTED")
    followers = Relationship("models.users.Customer", "FOLLOWS")
    location = Relationship("models.location.Location", "HAS")
