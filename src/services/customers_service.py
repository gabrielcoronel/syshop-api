import sanic
from sanic.exceptions import SanicException
from models.users import Customer
from utilities.sessions import create_session_for_user
from utilities.accounts import create_plain_account, fetch_google_account
from utilities.web import download_file_in_base64, validate_google_id_token

customers_service = sanic.Blueprint(
    "CustomersService",
    url_prefix="customers_service"
)


def split_google_raw_surnames(raw_surnames):
    split = raw_surnames.split(" ", 1)

    if len(split) == 1:
        return (split[0], "")

    return split


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


@customers_service.post("/sign_up_customer_with_plain_account")
def sign_up_customer_with_plain_account(request):
    email = request.json.pop("email")
    password = request.json.pop("password")

    plain_account = create_plain_account(email, password)
    customer = Customer(**request.json).save()

    customer.account.connect(plain_account)

    json = create_session_for_user(customer)

    return sanic.json(json)


@customers_service.post("/sign_on_customer_with_google_account")
def sign_on_customer_with_google_account(request):
    google_id_token = request.json["token"]

    (user_information, is_user_information_valid) = validate_google_id_token(
        google_id_token
    )

    if not is_user_information_valid:
        raise SanicException("Google ID token is invalid")

    google_account = fetch_google_account(user_information)

    if not google_account.user:
        customer = make_customer_from_google_user_information(user_information)
        customer.account.connect(google_account)
    else:
        customer = google_account.user

    json = create_session_for_user(customer)

    return sanic.json(json)


@customers_service.post("/update_customer")
def update_customer(request):
    customer_id = request.json.pop("customer_id")

    customer = Customer.nodes.first(user_id=customer_id)

    customer.name = request.json["name"]
    customer.first_lastname = request.json["first_lastname"]
    customer.second_lastname = request.json["second_lastname"]
    customer.picture = request.json["picture"]

    customer.save()

    return sanic.empty()


@customers_service.post("/get_customer_by_id")
def get_customer_by_id(request):
    customer_id = request.json["customer_id"]

    customer = Customer.nodes.first(user_id=customer_id)
    account_type = customer.__class__.__name__

    json = {
        **customer.__properties__,
        "account_type": account_type
    }

    return sanic.json(json)
