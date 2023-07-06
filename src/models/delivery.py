from neomodel import StructuredNode, DateTimeProperty, Relationship


class Delivery(StructuredNode):
    start_ride_datetime = DateTimeProperty(required=False)
    end_ride_datetime = DateTimeProperty(required=False)

    sale = Relationship("models.sale.Sale", "DELIVERS")
    location = Relationship("models.location.Location", "GOES_TO")
