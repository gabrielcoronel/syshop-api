from neomodel import StructuredNode, StringProperty


class PostMultimediaItem(StructuredNode):
    content_bytes = StringProperty(required=True)
