import sanic
import requests
import google
from base64 import b64encode
from os import getenv
from validate_email import validate_email
from sanic.exceptions import SanicException
from models.accounts import PlainAccount, GoogleAccount
from models.users import Customer
from models.session import Session
from utilities.encryption import encrypt, decrypt

customers_service = sanic.Blueprint(
    "CustomersService",
    url_prefix="customers_service"
)


def is_email_available(email):
    plain_account_or_none = PlainAccount.nodes.first_or_none(email=email)

    if plain_account_or_none is not None:
        return False

    is_valid = validate_email(email)

    return is_valid


def validate_google_id_token(token):
    google_api_client_id = getenv("GOOGLE_API_CLIENT_ID")

    try:
        user_information = google.oauth2.id_token.verify_oauth2_token(
            token,
            google.auth.transport.requests.Request(),
            google_api_client_id
        )

        return (user_information, True)
    except:
        return (None, False)


def split_google_raw_surnames(raw_surnames):
    split = raw_surnames.split(" ", 1)

    if len(split) == 1:
        return (split[0], "")

    return split


def download_file_in_base64(url):
    response = requests.get(url)
    base64_bytes = b64encode(response.content)
    base64_string = base64_bytes.decode("utf-8")

    return base64_string


def create_session_for_customer(customer):
    session = Session().save()

    session.user.connect(customer)

    json = {"token": session.token}

    return json


def fetch_google_signed_on_customer(user_information):
    google_unique_identifier = user_information["sub"]

    old_google_account_or_none = GoogleAccount.nodes.first_or_none(
        google_unique_identifier=google_unique_identifier
    )

    if old_google_account_or_none is not None:
        customer = old_google_account_or_none.user

        return customer

    new_google_account = GoogleAccount(
        google_unique_identifier=google_unique_identifier
    )

    customer = make_customer_from_google_user_information(user_information).save()
    customer.account.connect(new_google_account)

    return customer


def make_customer_from_google_user_information(user_information):
    picture_url = user_information["picture"]
    raw_surnames = user_information["family_name"]

    name = user_information["given_name"]
    picture = download_file_in_base64(picture_url)
    first_surname, second_surname = split_google_raw_surnames(raw_surnames)

    customer = Customer(
        name=name,
        first_surname=first_surname,
        second_surname=second_surname,
        picture=picture
    )

    return customer


@customers_service.post("/check_user_email_is_available")
def check_user_email_is_available(request):
    email = request.json["email"]

    exists = is_email_available(email)

    return sanic.json(exists)


@customers_service.post("/sign_up_customer_with_plain_account")
def sign_up_customer_with_plain_account(request):
    email = request.json.pop("email")
    password = request.json.pop("password")

    if not is_email_available(email):
        raise SanicException("Email is unavailable")

    encrypted_password = encrypt(password)

    plain_account = PlainAccount(
        email=email,
        password=encrypted_password
    ).save()
    customer = Customer(**request.json).save()

    customer.account.connect(plain_account)

    json = create_session_for_customer(customer)

    return sanic.json(json)


@customers_service.post("/sign_in_customer_with_plain_account")
def sign_in_customer_with_plain_account(request):
    email = request.json["email"]
    request_password = request.json["password"]

    customer = Customer.nodes.first(email=email)

    stored_password = decrypt(customer.password)

    if request_password != stored_password:
        raise SanicException("Incorrect password")

    json = create_session_for_customer(customer)

    return sanic.json(json)


@customers_service.post("/sign_on_customer_with_google_account")
def sign_on_customer_with_google_account(request):
    google_id_token = request.json["token"]

    (user_information, is_user_information_valid) = validate_google_id_token(
        google_id_token
    )

    if not is_user_information_valid:
        raise SanicException("Google ID token is invalid")

    customer = fetch_google_signed_on_customer(user_information)

    json = create_session_for_customer(customer)

    return sanic.json(json)


@customers_service.post("/get_customer_by_id")
def get_customer_by_id(request):
    customer_id = request.json["customer_id"]

    customer = Customer.nodes.first(user_id=customer_id)

    json = customer.__properties__

    return sanic.json(json)


@customers_service.post("/delete_customer")
def delete_customer(request):
    user_id = request.json["user_id"]

    customer = Customer.nodes.first(user_id=user_id)

    customer.account.first().delete()
    customer.delete()

    return sanic.empty()
