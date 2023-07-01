from neomodel import (
    StructuredNode,
    UniqueIdProperty,
    EmailProperty,
    StringProperty,
    Relationship
)
from models.users import BaseUser


class BaseAccount(StructuredNode):
    account_id = UniqueIdProperty()

    user = Relationship("BaseUser", "IDENTIFIES")


class PlainAccount(BaseAccount):
    email = EmailProperty(required=True)
    password = StringProperty(required=True)


class GoogleAccount(BaseAccount):
    google_unique_identifier = StringProperty(required=True)
