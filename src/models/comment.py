from neomodel import (
    StructuredNode,
    StringProperty,
    DateTimeProperty,
    UniqueIdProperty
)


class Comment(StructuredNode):
    comment_id = UniqueIdProperty()
    publication_date = DateTimeProperty(default_now=True)
    text = StringProperty(required=True)
