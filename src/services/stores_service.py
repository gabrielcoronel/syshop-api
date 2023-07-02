import sanic
from sanic.exceptions import SanicException
from models.users import Store
from models.store_multimedia_item import StoreMultimediaItem
from utilities.sessions import create_session_for_user
from utilities.accounts import create_plain_account, fetch_google_account
from utilities.web import download_file_in_base64, validate_google_id_token

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
    avatar_bytes = download_file_in_base64(picture_url)

    store = Store(
        name=name,
        description="",
        avatar_bytes=avatar_bytes
    )

    return store


@stores_service.post("/sign_up_store_with_plain_account")
def sign_up_store_with_plain_account(request):
    email = request.json.pop("email")
    password = request.json.pop("password")
    multimedia_items = request.json.pop("multimedia")

    plain_account = create_plain_account(email, password)
    store = Store(**request.json).save()

    store.account.connect(plain_account)

    create_store_multimedia_items(store, multimedia_items)

    json = create_session_for_user(store)

    return sanic.json(json)


@stores_service.post("/sign_on_store_with_google_account")
def sign_on_store_with_google_account(request):
    google_id_token = request.json["token"]

    (user_information, is_user_information_valid) = validate_google_id_token(
        google_id_token
    )

    if not is_user_information_valid:
        raise SanicException("Google ID token is invalid")

    google_account = fetch_google_account(user_information)

    if not google_account.user:
        store = make_store_from_google_user_information(user_information)
        store.account.connect(google_account)
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
    store.avatar_bytes = request.json["avatar"]

    store.save()

    return sanic.empty()


@stores_service.post("/get_store_by_id")
def get_store_by_id(request):
    store_id = request.json["store_id"]

    store = Store.nodes.first(user_id=store_id)
    multimedia_items = [
        store_multimedia_item.content_bytes
        for store_multimedia_item in store.multimedia.all()
    ]
    account_type = store.__class__.__name__

    json = {
        **store.__properties__,
        "multimedia": multimedia_items,
        "account_type": account_type
    }

    return sanic.json(json)
