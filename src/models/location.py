from neomodel import (
    StructuredNode,
    StringProperty,
    FloatProperty,
    UniqueIdProperty,
    Relationship
)


class Location(StructuredNode):
    location_id = UniqueIdProperty()
    place_name = StringProperty(required=True)
    street_address = StringProperty(required=True)
    city = StringProperty(required=True)
    state = StringProperty(required=True)
    zip_code = StringProperty(required=True)
    latitude = FloatProperty(required=True)
    longitude = FloatProperty(required=True)

    user = Relationship("models.users.BaseUser", "HAS")
