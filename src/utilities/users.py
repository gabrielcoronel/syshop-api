def get_user_websocket_connections_ids(user):
    stored_connections = user.websocket_connections.all()
    connections_ids = [
        connection.connection_id
        for connection in stored_connections
    ]

    return connections_ids
