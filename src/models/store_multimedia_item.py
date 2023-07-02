from neomodel import StructuredNode, StringProperty


class StoreMultimediaItem(StructuredNode):
    content_bytes = StringProperty(required=True)
