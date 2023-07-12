from models.session import Session


def create_session_for_user(user):
    session = Session().save()

    session.user.connect(user)

    json = {
        "token": session.token,
        "user_id": user.user_id
    }

    return json
