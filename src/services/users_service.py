import sanic
from sanic.exceptions import SanicException
from models.accounts import PlainAccount, GoogleAccount
from models.users import BaseUser
from models.session import Session
from utilities.encryption import encrypt, decrypt
from utilities.sessions import create_session_for_user
from utilities.accounts import is_plain_account_email_available


users_service = sanic.Blueprint(
    "UsersService",
    url_prefix="/users_service"
)


def is_password_correct(plain_account, password):
    stored_password = decrypt(plain_account.password)
    print(stored_password)

    return password == stored_password


@users_service.post("/check_user_email_is_available")
def check_user_email_is_available(request):
    email = request.json["email"]

    exists = is_plain_account_email_available(email)

    return sanic.json(exists)


@users_service.post("/sign_in_user_with_plain_account")
def sign_in_user_with_plain_account(request):
    email = request.json["email"]
    request_password = request.json["password"]

    plain_account = PlainAccount.nodes.first(email=email)

    if not is_password_correct(plain_account, request_password):
        raise SanicException("Incorrect password")

    user = plain_account.user.single()

    json = create_session_for_user(user)

    return sanic.json(json)

@users_service.post("/sign_in_user_with_google_account")
def sign_in_user_with_google_account(request):
    google_unique_identifier = request.json["google_unique_identifier"]

    google_account = GoogleAccount.nodes.first(
        google_unique_identifier=google_unique_identifier
    )

    user = google_account.user.single()

    json = create_session_for_user(user)

    return sanic.json(json)


@users_service.post("/close_user_session")
def close_user_session(request):
    token = request.json["token"]

    session = Session.nodes.first(token=token)
    session.delete()

    return sanic.empty()


@users_service.post("/change_user_email")
def change_user_email(request):
    user_id = request.json["user_id"]
    password = request.json["password"]
    new_email = request.json["email"]

    plain_account = BaseUser.nodes.first(user_id=user_id).account.single()

    if not is_password_correct(plain_account, password):
        raise SanicException("Incorrect password")

    plain_account.email = new_email
    plain_account.save()

    return sanic.empty()


@users_service.post("/change_user_password")
def change_user_password(request):
    user_id = request.json["user_id"]
    old_password = request.json["old_password"]
    new_password = request.json["new_password"]

    plain_account = BaseUser.nodes.first(user_id=user_id).account.single()

    if not is_password_correct(plain_account, old_password):
        raise SanicException("Incorrect password")

    plain_account.password = encrypt(new_password)
    plain_account.save()

    return sanic.empty()


@users_service.post("/delete_user")
def delete_user(request):
    user_id = request.json["user_id"]

    user = BaseUser.nodes.first(user_id=user_id)

    user.account.single().delete()

    for session in user.sessions.all():
        session.delete()

    user.delete()

    return sanic.empty()
