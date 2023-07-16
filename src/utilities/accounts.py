from sanic.exceptions import SanicException
from models.accounts import GoogleAccount, PlainAccount
from validate_email import validate_email
from utilities.encryption import encrypt


def is_plain_account_email_available(email):
    plain_account_or_none = PlainAccount.nodes.first_or_none(email=email)

    if plain_account_or_none is not None:
        return False

    is_valid = validate_email(email)

    return is_valid


def create_plain_account(email, password):
    if not is_plain_account_email_available(email):
        raise SanicException("Email is unavailable")

    encrypted_password = encrypt(password)

    plain_account = PlainAccount(
        email=email,
        password=encrypted_password
    ).save()

    return plain_account


def fetch_google_account(user_information):
    google_unique_identifier = user_information["id"]

    google_account = GoogleAccount.get_or_create({
        "google_unique_identifier": google_unique_identifier
    })[0]

    return google_account
