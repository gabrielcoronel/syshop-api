from neomodel import StructuredNode, DateTimeProperty


class Delivery(StructuredNode):
    start_ride_datetime = DateTimeProperty(required=False)
    end_ride_datetime = DateTimeProperty(required=False)
