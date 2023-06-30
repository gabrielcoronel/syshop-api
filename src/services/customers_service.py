import sanic
from models.accounts import PlainAccount
from models.customer import Customer
from models.session import Session
from utilities.encryption import encrypt


customers_service = sanic.Blueprint(
    "CustomersService",
    url_prefix="customers_service"
)


@customers_service.post("/sign_up_customer_with_plain_account")
def sign_up_customer_with_plain_account(request):
    email = request.json.pop("email")
    password = request.json.pop("password")
    encrypted_password = encrypt(password)

    plain_account = PlainAccount(email=email, password=encrypted_password).save()
    customer = Customer(**request.json).save()

    customer.account.connect(plain_account)

    session = Session().save()
    json = {"token": session.token}

    return sanic.json(json)
