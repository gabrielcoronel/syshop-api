from neomodel import StructuredNode, StringProperty


class Category(StructuredNode):
    name = StringProperty(required=True)
