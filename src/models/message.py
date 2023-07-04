from neomodel import (
    StructuredNode,
    StringProperty,
    DateTimeProperty,
    UniqueIdProperty,
    Relationship
)


class Message(StructuredNode):
    message_id = UniqueIdProperty()
    content_type = StringProperty(required=True)
    content = StringProperty(required=True)
    sent_datetime = DateTimeProperty(default_now=True)

    user = Relationship("models.users.BaseUser", "SENT")
