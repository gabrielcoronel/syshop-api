from neomodel import (
    StructuredNode,
    StringProperty,
    DateTimeProperty,
    UniqueIdProperty,
    Relationship
)


class Comment(StructuredNode):
    comment_id = UniqueIdProperty()
    publication_date = DateTimeProperty(default_now=True)
    text = StringProperty(required=True)

    user = Relationship("models.users.BaseUser", "COMMENTS")
