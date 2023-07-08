from neomodel import StructuredNode, UniqueIdProperty


class WebsocketConnection(StructuredNode):
    connection_id = UniqueIdProperty()
