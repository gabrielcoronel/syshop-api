from neomodel import (
    StructuredNode,
    StringProperty,
    DateTimeProperty,
    UniqueIdProperty,
    Relationship
)

class Report(StructuredNode):
    report_id = UniqueIdProperty()
    content = StringProperty(required=True)
    created_datetime = DateTimeProperty(default_now=True)

    user = Relationship("models.users.BaseUser", "CREATED")
