from neomodel import StructuredNode, DateTimeProperty


class DeliveryModel(StructuredNode):
    issue_date = DateTimeProperty(required=True)
    delivery_date = DateTimeProperty(required=False)
