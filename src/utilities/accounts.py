from sanic.exceptions import SanicException
from models.accounts import GoogleAccount, PlainAccount
from validate_email import validate_email
from utilities.encryption import encrypt


def is_plain_account_email_available(email):
    plain_account_or_none = PlainAccount.nodes.first_or_none(email=email)

    if plain_account_or_none is not None:
        return False

    return True


def create_plain_account(email, password):
    if not is_plain_account_email_available(email):
        raise SanicException("UNAVAILABLE_EMAIL")

    encrypted_password = encrypt(password)

    plain_account = PlainAccount(
        email=email,
        password=encrypted_password
    ).save()

    return plain_account


def does_google_account_exist(google_unique_identifier):
    existing_google_account_or_none = GoogleAccount.nodes.first_or_none(
        google_unique_identifier=google_unique_identifier
    )

    return existing_google_account_or_none is not None
