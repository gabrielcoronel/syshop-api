import sanic
from sanic.exceptions import SanicException
from models.users import Store, Customer
from models.location import Location
from models.store_multimedia_item import StoreMultimediaItem
from utilities.sessions import create_session_for_user
from utilities.accounts import create_plain_account, fetch_google_account
from utilities.web import download_file_in_base64
from utilities.stripe import create_stripe_account

stores_service = sanic.Blueprint(
    "StoresService",
    url_prefix="stores_service"
)


def create_store_multimedia_items(store, content_bytes_list):
    for content_bytes in content_bytes_list:
        store_multimedia_item = StoreMultimediaItem(
            content_bytes=content_bytes
        ).save()

        store.multimedia.connect(store_multimedia_item)


def make_store_from_google_user_information(user_information):
    picture_url = user_information["picture"]

    name = user_information["given_name"]
    phone_number = user_information["phone_number"]
    picture = download_file_in_base64(picture_url)
    stripe_account = create_stripe_account()

    store = Store(
        name=name,
        description="",
        picture=picture,
        phone_number=phone_number,
        stripe_account_id=stripe_account["id"]
    ).save()

    return store


@stores_service.post("/sign_up_store_with_plain_account")
def sign_up_store_with_plain_account(request):
    email = request.json.pop("email")
    password = request.json.pop("password")
    multimedia_items = request.json.pop("multimedia")

    plain_account = create_plain_account(email, password)
    stripe_account = create_stripe_account()
    store = Store(
        name=request.json.pop("name"),
        description=request.json.pop("description"),
        picture=request.json.pop("picture"),
        phone_number=request.json.pop("phone_number"),
        stripe_account_id=stripe_account["id"]
    ).save()
    location = Location(
        **request.json
    ).save()

    store.account.connect(plain_account)
    store.location.connect(location)

    create_store_multimedia_items(store, multimedia_items)

    json = create_session_for_user(store)

    return sanic.json(json)


@stores_service.post("/sign_on_store_with_google_account")
def sign_on_store_with_google_account(request):
    # user_information tiene que incluir un número de teléfono,
    # esto es responsabilidad del cliente
    user_information = request.json["user_information"]
    store_location = request.json["location"]

    google_account = fetch_google_account(user_information)

    if not google_account.user:
        store = make_store_from_google_user_information(user_information)
        location = Location(**store_location).save()

        store.account.connect(google_account)
        store.location.connect(location)
    else:
        store = google_account.user

    json = create_session_for_user(store)

    return sanic.json(json)


@stores_service.post("/update_store")
def update_store(request):
    store_id = request.json.pop("store_id")
    multimedia_items = request.json.pop("multimedia")

    store = Store.nodes.first(user_id=store_id)

    for store_multimedia_item in store.multimedia.all():
        store_multimedia_item.delete()

    create_store_multimedia_items(store, multimedia_items)

    store.name = request.json["name"]
    store.description = request.json["description"]
    store.phone_number = request.json["phone_number"]
    store.picture = request.json["picture"]

    store.save()

    return sanic.empty()


@stores_service.post("/follow_store")
def follow_store(request):
    store_id = request.json["store_id"]
    customer_id = request.json["customer_id"]

    customer = Customer.nodes.first(user_id=customer_id)
    store = Store.nodes.first(user_id=store_id)

    store.followers.connect(customer)

    return sanic.empty()


@stores_service.post("/get_store_by_id")
def get_store_by_id(request):
    store_id = request.json["store_id"]

    store = Store.nodes.first(user_id=store_id)
    multimedia_items = [
        store_multimedia_item.content_bytes
        for store_multimedia_item in store.multimedia.all()
    ]
    account_type = store.account.single().__class__.__name__

    json = {
        **store.__properties__,
        "multimedia": multimedia_items,
        "account_type": account_type
    }

    return sanic.json(json)


@stores_service.post("/search_stores_by_name")
def search_stores_by_name(request):
    start = request.json["start"]
    amount = request.json["amount"]
    searched_name = request.json["search"]

    search_results = Store.nodes.filter(
        name__icontains=searched_name
    )[start:amount]

    json = [
        store.__properties__
        for store in search_results
    ]

    return sanic.json(json)
