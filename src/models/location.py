from neomodel import (
    StructuredNode,
    StringProperty,
    FloatProperty,
    UniqueIdProperty,
    Relationship
)


class Location(StructuredNode):
    location_id = UniqueIdProperty()
    name = StringProperty(required=True)
    longitude = FloatProperty(required=True)
    latitude = FloatProperty(required=True)

    customer = Relationship("models.users.Customer", "HAS")
