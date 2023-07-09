from neomodel import (
    StructuredNode,
    BooleanProperty,
    StringProperty,
    UniqueIdProperty,
    Relationship
)


class Delivery(StructuredNode):
    delivery_id = UniqueIdProperty()
    is_active = BooleanProperty(required=True)
    uber_state = StringProperty(required=False)
    uber_delivery_id = StringProperty(required=False)
    uber_tracking_url = StringProperty(required=False)

    sale = Relationship("models.sale.Sale", "DELIVERS")
    location = Relationship("models.location.Location", "GOES_TO")
