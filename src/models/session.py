from neomodel import StructuredNode, UniqueIdProperty, Relationship
from models.users import BaseUser


class Session(StructuredNode):
    token = UniqueIdProperty()

    user = Relationship("BaseUser", "HOLDS")
