from neomodel import StructuredNode, StringProperty


class PostMultimediaModel(StructuredNode):
    content_bytes = StringProperty(required=True)
