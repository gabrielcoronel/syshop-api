from neomodel import (
    StructuredNode,
    UniqueIdProperty,
    EmailProperty,
    StringProperty
)


class BaseAccount(StructuredNode):
    account_id = UniqueIdProperty()


class PlainAccount(BaseAccount):
    email = EmailProperty(required=True)
    password = StringProperty(required=True)
