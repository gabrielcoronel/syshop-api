import sanic
from sanic.exceptions import SanicException
from models.users import Customer
from models.accounts import GoogleAccount
from utilities.sessions import create_session_for_user
from utilities.accounts import create_plain_account, does_google_account_exist
from utilities.web import download_file_in_base64

customers_service = sanic.Blueprint(
    "CustomersService",
    url_prefix="customers_service"
)


def split_google_raw_surnames(raw_surnames):
    split = raw_surnames.split(" ", 1)

    if len(split) == 1:
        return (split[0], "")

    return split

@customers_service.post("/sign_up_customer_with_plain_account")
def sign_up_customer_with_plain_account(request):
    email = request.json.pop("email")
    password = request.json.pop("password")

    plain_account = create_plain_account(email, password)
    customer = Customer(**request.json).save()

    customer.account.connect(plain_account)

    json = create_session_for_user(customer)

    return sanic.json(json)


@customers_service.post("/sign_up_customer_with_google_account")
def sign_up_customer_with_google_account(request):
    google_unique_identifier = request.json.pop("google_unique_identifier")
    google_picture_url = request.json.pop("picture")

    if does_google_account_exist(google_unique_identifier):
        raise SanicException("GOOGLE_ACCOUNT_ALREADY_EXISTS")

    picture = download_file_in_base64(google_picture_url)
    customer = Customer(**request.json, picture=picture).save()
    google_account = GoogleAccount(
        google_unique_identifier=google_unique_identifier
    ).save()

    customer.account.connect(google_account)

    json = create_session_for_user(customer)

    return sanic.json(json)


@customers_service.post("/update_customer")
def update_customer(request):
    customer_id = request.json.pop("customer_id")

    customer = Customer.nodes.first(user_id=customer_id)

    customer.name = request.json["name"]
    customer.first_surname = request.json["first_surname"]
    customer.second_surname = request.json["second_surname"]
    customer.phone_number = request.json["phone_number"]
    customer.picture = request.json["picture"]

    customer.save()

    return sanic.empty()


@customers_service.post("/get_customer_by_id")
def get_customer_by_id(request):
    customer_id = request.json["customer_id"]

    customer = Customer.nodes.first(user_id=customer_id)
    account = customer.account.single()
    account_type = account.__class__.__name__

    json = {
        **customer.__properties__,
        "email": account.email if account_type == "PlainAccount" else None,
        "account_type": account_type
    }

    return sanic.json(json)
