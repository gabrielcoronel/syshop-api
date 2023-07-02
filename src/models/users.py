from neomodel import (
    StructuredNode,
    StringProperty,
    UniqueIdProperty,
    Relationship
)
from models.accounts import BaseAccount
from models.store_multimedia_item import StoreMultimediaItem


class BaseUser(StructuredNode):
    user_id = UniqueIdProperty(required=True)

    account = Relationship("BaseAccount", "IDENTIFIES")


class Customer(BaseUser):
    name = StringProperty(required=True)
    first_surname = StringProperty(required=True)
    second_surname = StringProperty(required=True)
    picture = StringProperty(required=False)


class Store(BaseUser):
    name = StringProperty(required=True)
    description = StringProperty(required=True)
    avatar_bytes = StringProperty(required=True)

    multimedia = Relationship("StoreMultimediaItem", "HAS")
