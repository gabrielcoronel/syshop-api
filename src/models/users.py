from neomodel import (
    StructuredNode,
    StringProperty,
    UniqueIdProperty,
    Relationship
)
from models.store_multimedia_item import StoreMultimediaItem


class BaseUser(StructuredNode):
    user_id = UniqueIdProperty()

    account = Relationship("models.accounts.BaseAccount", "IDENTIFIES")
    sessions = Relationship("models.session.Session", "HOLDS")


class Customer(BaseUser):
    name = StringProperty(required=True)
    first_surname = StringProperty(required=True)
    second_surname = StringProperty(required=True)
    picture = StringProperty(required=False)

    locations = Relationship("models.location.Location", "HAS")


class Store(BaseUser):
    name = StringProperty(required=True)
    description = StringProperty(required=True)
    avatar = StringProperty(required=True)

    multimedia = Relationship("StoreMultimediaItem", "HAS")
