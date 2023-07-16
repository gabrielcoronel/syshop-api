import orjson

connection_registry = dict()


def register_connection(connection, connection_id):
    connection_registry[connection_id] = connection


def dispatch_event(event_payload, connections_ids):
    connections = [
        connection_registry[id]
        for id in connections_ids
    ]

    for connection in connections:
        message = orjson.dumps(event_payload)

        connection.send(message)
