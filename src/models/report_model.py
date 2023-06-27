from neomodel import StructuredNode, StringProperty


class ReportModel(StructuredNode):
    description = StringProperty(required=True)
