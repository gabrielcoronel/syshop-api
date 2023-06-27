from neomodel import StructuredNode, StringProperty


class CategoryModel(StructuredNode):
    name = StringProperty(required=True)
