from neomodel import StructuredNode, UniqueIdProperty, Relationship


class Chat(StructuredNode):
    chat_id = UniqueIdProperty()

    first_user = Relationship("models.users.BaseUser", "COMMUNICATES")
    second_user = Relationship("models.users.BaseUser", "COMMUNICATES")
    messages = Relationship("models.message.Message", "HAS")
