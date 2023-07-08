import sanic
from models.users import BaseUser
from models.websocket_connection import WebsocketConnection
from utilities.events_dispatching import register_connection

event_dispatcher_service = sanic.Blueprint(
    "EventDispatcherService";
    url_prefix="/event_dispatcher_service"
)


@event_dispatcher_service.websocket("/subscribe_to_event_dispatcher")
async def subscribe_to_event_dispatcher(request, connection):
    user_id = await connection.recv()

    user = BaseUser.nodes.first(user_id=user_id)
    stored_connection = WebsocketConnection().save()

    user.websocket_connections.connect(stored_connection)

    register_connection(connection, stored_connection.connection_id)
