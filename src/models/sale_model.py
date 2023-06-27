from neomodel import StructuredNode, DateTimeProperty


class SaleModel(StructuredNode):
    sale_date = DateTimeProperty(required=True)
