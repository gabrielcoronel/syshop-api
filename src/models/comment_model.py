from neomodel import StructuredNode, StringProperty, DateTimeProperty


class CommentModel(StructuredNode):
    publication_date = DateTimeProperty(default_now=True)
    text = StringProperty(required=True)
