import sanic
from neomodel import db
from sanic.exceptions import SanicException
from models.users import BaseUser
from models.chat import Chat
from models.message import Message
from utilities.event_dispatching import dispatch_event
from utilities.users import (
    get_user_websocket_connections_ids,
    format_user_name
)

chat_service = sanic.Blueprint(
    "ChatService",
    url_prefix="/chat_service"
)


def get_chat_messages(chat):
    messages = chat.messages.order_by("-sent_datetime")

    return messages


def fetch_user_chats(user):
    query = """
    MATCH (:BaseUser {user_id: $user_id})-[:COMMUNICATES]-(c:Chat)-[:HAS]-(m:Message)
    MATCH (c)-[:COMMUNICATES]-(r:BaseUser)
    WHERE r.user_id <> $user_id
    WITH c AS chat, r AS receiver, m.sent_datetime as datetime
    ORDER BY datetime
    RETURN DISTINCT chat, receiver
    """

    result, _ = db.cypher_query(
        query,
        {
            "user_id": user.user_id
        },
        resolve_objects=True
    )

    chats = [
        (row[0], row[1])
        for row in result
    ]

    return chats


def make_chat_json_view(chat, user):
    (actual_chat, receiver) = chat

    last_message = get_chat_messages(actual_chat)[0]

    json = {
        **actual_chat.__properties__,
        "user": {
            "picture": receiver.picture,
            "name": format_user_name(receiver),
            "user_id": receiver.user_id,
            "phone_number": receiver.phone_number
        },
        "last_message": last_message.__properties__
    }

    return json


def make_message_json_view(message):
    user = message.user.single()

    json = {
        **message.__properties__,
        "user_id": user.user_id
    }

    return json


def fetch_chat(sender, receiver):
    query = """
    MATCH (s:BaseUser {user_id: $sender_id})-[:COMMUNICATES]-(c:Chat)
    MATCH (c)-[:COMMUNICATES]-(r:BaseUser {user_id: $receiver_id})
    WHERE s.user_id <> r.user_id
    RETURN c AS chat
    LIMIT 1
    """

    result, _ = db.cypher_query(
        query,
        {
            "sender_id": sender.user_id,
            "receiver_id": receiver.user_id,
        },
        resolve_objects=True
    )

    if len(result) == 0:
        chat = Chat().save()

        chat.first_user.connect(sender)
        chat.second_user.connect(receiver)
    else:
        chat = result[0][0]

    return chat


@chat_service.post("/get_user_chats")
def get_user_chats(request):
    user_id = request.json["user_id"]

    user = BaseUser.nodes.first(user_id=user_id)
    chats = fetch_user_chats(user)

    json = [
        make_chat_json_view(chat, user)
        for chat in chats
    ]

    return sanic.json(json)


@chat_service.post("/get_chat_by_id")
def get_chat_by_id(request):
    chat_id = request.json["chat_id"]

    chat = Chat.nodes.first(chat_id=chat_id)
    messages = get_chat_messages(chat)

    json = [
        make_message_json_view(message)
        for message in messages
    ]

    return sanic.json(json)


@chat_service.post("/get_chat_by_sender_and_receiver")
def get_chat_by_sender_and_receiver(request):
    sender_id = request.json["sender_id"]
    receiver_id = request.json["receiver_id"]

    query = """
    MATCH (:BaseUser {user_id: $sender_id})-[:COMMUNICATES]->(c:Chat)<-[:COMMUNICATES]-(:BaseUser {user_id: $receiver_id})
    RETURN c AS chat
    LIMIT 1
    """

    result, _ = db.cypher_query(
        query,
        {
            "sender_id": sender_id,
            "receiver_id": receiver_id
        },
        resolve_objects=True
    )

    if len(result) == 0:
        return sanic.json(None)

    chat = result[0][0]
    json = chat.__properties__

    return sanic.json(json)


@chat_service.post("/add_message")
def add_message(request):
    sender_id = request.json.pop("sender_id")
    receiver_id = request.json.pop("receiver_id")

    sender = BaseUser.nodes.first(user_id=sender_id)
    receiver = BaseUser.nodes.first(user_id=receiver_id)
    message = Message(**request.json).save()
    chat = fetch_chat(sender, receiver)

    message.user.connect(sender)
    chat.messages.connect(message)

    websocket_connections_ids = ([
        *get_user_websocket_connections_ids(sender),
        *get_user_websocket_connections_ids(receiver)
    ])

    dispatch_event(
        {
            "type": "chat.message.added"
        },
        websocket_connections_ids
    )

    return sanic.empty()


@chat_service.post("/edit_message")
def edit_message(request):
    message_id = request.json["message_id"]

    message = Message.nodes.first(message_id=message_id)

    if message.content_type.lower() != "text":
        # Diseñe bien el frontend, para que esto no pase
        raise SanicException("EDIT_NON_TEXT_MESSAGE")

    message.content = request.json["content"]
    message.save()

    user = message.user.single()

    websocket_connections_ids = get_user_websocket_connections_ids(user)

    dispatch_event(
        {
            "type": "chat.message.edited"
        },
        websocket_connections_ids
    )

    return sanic.empty()


@chat_service.post("/delete_message")
def delete_message(request):
    message_id = request.json["message_id"]

    message = Message.nodes.first(message_id=message_id)
    user = message.user.single()

    message.delete()

    websocket_connections_ids = get_user_websocket_connections_ids(user)

    dispatch_event(
        {
            "type": "chat.message.deleted"
        },
        websocket_connections_ids
    )

    return sanic.empty()
