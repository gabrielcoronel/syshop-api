import sanic
from sanic.exceptions import SanicException
from models.users import BaseUser
from models.chat import Chat
from models.message import Message

chat_service = sanic.Blueprint(
    "ChatService",
    url_prefix="/chat_service"
)


def format_user_name(user):
    user_type = user.__class__.__name__

    match user_type:
        case "Customer":
            return f"{user.name} {user.first_surname} {user.second_surname}"
        case "Store":
            return user.name
        case _:
            raise ValueError("Estado inválido: esto es culpa del programador")


def get_chat_messages(chat):
    messages = chat.messages.order_by("-sent_datetime")

    return messages


def make_chat_json_view(chat, user):
    if chat.first_user.single().user_id == user.user_id:
        receiving_user = chat.second_user.single()
    else:
        receiving_user = chat.first_user.single()

    last_message = get_chat_messages(chat)[0]

    json = {
        "picture": receiving_user.picture,
        "user_name": format_user_name(receiving_user),
        "last_message_sent": last_message.sent_datetime,
        "last_message_content_type": last_message.content_type,
        "last_message_content": last_message.content
    }

    return json


def make_message_json_view(message):
    user = message.user.single()

    user_name = format_user_name(user)

    json = {
        **message.__properties__,
        "user_name": user_name
    }

    return json


def fetch_chat(sender, receiver):
    matched_chats = [
        chat
        for chat in sender.chats.all()
        if (chat.first_user.single().user_id == receiver.user_id)
        or (chat.second_user.single().user_id == receiver.user_id)
    ]

    if len(matched_chats) == 0:
        chat = Chat().save()
        chat.first_user.connect(sender)
        chat.second_user.connect(receiver)
    else:
        chat = matched_chats[0]

    return chat


@chat_service.post("get_user_chats")
def get_user_chats(request):
    user_id = request.json["user_id"]

    user = BaseUser.nodes.first(user_id=user_id)
    chats = user.chats.all()

    json = [
        make_chat_json_view(chat, user)
        for chat in chats
    ]

    return sanic.json(json)


@chat_service.post("get_chat_by_id")
def get_chat_by_id(request):
    chat_id = request.json["chat_id"]

    chat = Chat.nodes.first(chat_id=chat_id)
    messages = get_chat_messages(chat)

    json = [
        make_message_json_view(message)
        for message in messages
    ]

    return sanic.json(json)


@chat_service.post("add_message")
def add_message(request):
    sender_id = request.json.pop("sender_id")
    receiver_id = request.json.pop("receiver_id")

    sender = BaseUser.nodes.first(user_id=sender_id)
    receiver = BaseUser.nodes.first(user_id=receiver_id)
    message = Message(**request.json).save()
    chat = fetch_chat(sender, receiver)

    message.user.connect(sender)
    chat.messages.connect(message)

    return sanic.empty()


@chat_service.post("edit_message")
def edit_message(request):
    message_id = request.json["message_id"]

    message = Message.nodes.first(message_id=message_id)

    if message.content_type.lower() != "text":
        raise SanicException("Cannot edit non-text messages")

    message.content = request.json["content"]
    message.save()

    return sanic.empty()


@chat_service.post("delete_message")
def delete_message(request):
    message_id = request.json["message_id"]

    message = Message.nodes.first(message_id=message_id)
    message.delete()

    return sanic.empty()
