def get_user_websocket_connections_ids(user):
    stored_connections = user.websocket_connections.all()
    connections_ids = [
        connection.connection_id
        for connection in stored_connections
    ]

    return connections_ids


def format_user_name(user):
    user_type = user.__class__.__name__

    print("format_user_name", user_type)

    match user_type:
        case "Customer":
            return f"{user.name} {user.first_surname} {user.second_surname}"
        case "Store":
            return user.name
        case _:
            raise ValueError("Estado inválido: esto es culpa del programador")
