from neomodel import StructuredNode, StringProperty


class StoreMultimediaModel(StructuredNode):
    content_bytes = StringProperty(required=True)
