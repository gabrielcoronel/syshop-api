from neomodel import StructuredNode, DateTimeProperty


class Sale(StructuredNode):
    sale_date = DateTimeProperty(required=True)
