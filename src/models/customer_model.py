from neomodel import StructuredNode, StringProperty


class CustomerModel(StructuredNode):
    name = StringProperty(required=True)
    first_surname = StringProperty(required=True)
    second_surname = StringProperty(required=True)
