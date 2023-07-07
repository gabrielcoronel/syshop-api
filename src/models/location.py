from neomodel import (
    StructuredNode,
    StringProperty,
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

    customer = Relationship("models.users.Customer", "HAS")
