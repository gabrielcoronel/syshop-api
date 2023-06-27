from neomodel import StructuredNode, StringProperty


class StoreModel:
    name = StringProperty(required=True)
    description = StringProperty(required=True)
    avatar_bytes = StringProperty(required=True)
