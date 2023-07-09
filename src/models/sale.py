from neomodel import (
    StructuredNode,
    IntegerProperty,
    DateTimeProperty,
    UniqueIdProperty,
    Relationship
)


class Sale(StructuredNode):
    sale_id = UniqueIdProperty()
    sale_date = DateTimeProperty(required=True)
    amount = IntegerProperty(required=True)

    post = Relationship("models.sale.Sale", "SOLD")
    delivery = Relationship("models.delivery.Delivery", "DELIVERS")
