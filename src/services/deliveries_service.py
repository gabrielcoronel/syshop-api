import sanic
import sanic.exceptions
import hashlib
import hmac
from os import getenv
from neomodel import db
from sanic.exceptions import SanicException
from models.sale import Sale
from models.users import Store, Customer
from models.location import Location
from models.delivery import Delivery
from utilities.uber import start_uber_delivery
from utilities.event_dispatching import dispatch_event

deliveries_service = sanic.Blueprint(
    "DeliveryService",
    url_prefix="/deliveries_service"
)


def make_delivery_json_view(delivery):
    sale = delivery.sale.single()
    post = sale.post.single()
    location = delivery.location.single()

    json = {
        **delivery.__properties__,
        "post": post.__properties__,
        "sale": sale.__properties__,
        "location": location.__properties__
    }

    return json


def get_store_from_delivery(delivery):
    sale = delivery.sale.single()
    post = sale.post.single()
    store = post.store.single()

    return store


def get_deliveries_from_sales(sales):
    deliveries = [
        sale.delivery.single()
        for sale in sales
        if sale.delivery.single() is not None
    ]

    return deliveries


def is_uber_webhook_payload_safe(payload, signature):
    secret = getenv("UBER_DELIVERY_STATUS_WEBHOOK_SECRET")
    hmac_hasher = hmac.new(secret, str(payload), hashlib.sha256)
    generated_hash = hmac_hasher.hexdigest()

    return generated_hash == signature


def get_websocket_connections_ids_from_delivery(delivery):
    query =  """
    MATCH (u:BaseUser)-[:BOUGHT|SOLD]-(:Sale)-[:DELIVERS]-(:Delivery {delivery_id: $delivery_id})
    MATCH (c:WebsocketConnection)-[:LISTENS]-(u)
    RETURN c.connection_id AS connections_ids
    """

    connections_ids, _ = db.cypher_query(
        query,
        {
            "delivery_id": delivery.delivery_id
        }
    )

    return connections_ids


@deliveries_service.post("/create_delivery")
def create_delivery(request):
    sale_id = request.json["sale_id"]
    location_id = request.json["location_id"]

    sale = Sale.nodes.first(sale_id=sale_id)
    location = Location.nodes.first(location_id=location_id)
    delivery = Delivery(
        is_active=False,
        uber_state=None,
        uber_delivery_id=None,
        uber_tracking_url=None
    ).save()

    delivery.sale.connect(sale)
    delivery.location.connect(location)

    return sanic.empty()


@deliveries_service.post("/activate_delivery")
def activate_delivery(request):
    delivery_id = request.json["delivery_id"]

    delivery = Delivery.nodes.first(delivery_id=delivery_id)
    store = get_store_from_delivery(delivery)
    store_location_or_none = store.location.single()
    sale = delivery.sale.single()
    customer_location = delivery.location.single()
    customer = customer_location.user.single()

    if store_location_or_none is None:
        # Diseñe bien el frontend, para que esto no pase
        raise SanicException("STORE_LOCATION_NOT_FOUND")

    delivery_response = start_uber_delivery(
        customer,
        customer_location,
        store,
        store_location_or_none,
        sale
    )

    delivery.is_active = True
    delivery.uber_state = delivery_response["status"]
    delivery.uber_delivery_id = delivery_response["id"]
    delivery.uber_tracking_url = delivery_response["tracking_url"]
    delivery.save()

    return sanic.empty()


@deliveries_service.post("/get_store_inactive_deliveries")
def get_store_inactive_deliveries(request):
    store_id = request.json["store_id"]

    store = Store.nodes.first(user_id=store_id)
    sales = store.sales.all()
    deliveries = get_deliveries_from_sales(sales)
    inactive_deliveries = filter(lambda d: not d.is_active, deliveries)

    json = [
        make_delivery_json_view(delivery)
        for delivery in inactive_deliveries
    ]

    return sanic.json(json)


@deliveries_service.post("/get_store_active_deliveries")
def get_store_active_deliveries(request):
    store_id = request.json["store_id"]

    store = Store.nodes.first(user_id=store_id)
    sales = store.sales.all()
    deliveries = get_deliveries_from_sales(sales)
    inactive_deliveries = filter(lambda d: d.is_active, deliveries)

    json = [
        make_delivery_json_view(delivery)
        for delivery in inactive_deliveries
    ]

    return sanic.json(json)


@deliveries_service.post("/get_customer_inactive_deliveries")
def get_customer_inactive_deliveries(request):
    customer_id = request.json["customer_id"]

    customer = Customer.nodes.first(user_id=customer_id)
    purchases = customer.purchases.all()
    deliveries = get_deliveries_from_sales(purchases)
    inactive_deliveries = filter(lambda d: not d.is_active, deliveries)

    json = [
        make_delivery_json_view(delivery)
        for delivery in inactive_deliveries
    ]

    return sanic.json(json)


@deliveries_service.post("/get_customer_active_deliveries")
def get_customer_active_deliveries(request):
    customer_id = request.json["customer_id"]

    customer = Customer.nodes.first(user_id=customer_id)
    purchases = customer.purchases.all()
    deliveries = get_deliveries_from_sales(purchases)
    active_deliveries = filter(lambda d: d.is_active, deliveries)

    json = [
        make_delivery_json_view(delivery)
        for delivery in active_deliveries
    ]

    return sanic.json(json)


@deliveries_service.post("/uber_delivery_status_webhook")
def uber_delivery_status_webhook(request):
    payload = request.json
    signature = request.headers["X-Postmates-Signature"]

    if not is_uber_webhook_payload_safe(payload, signature):
        # Esperemos que no pase
        raise SanicException("UNSAFE_UBER_PAYLOAD_OR_SIGNATURE")

    new_uber_state = payload["status"]
    uber_delivery_id = payload["data"]["id"]

    delivery = Delivery.nodes.first(uber_delivery_id=uber_delivery_id)

    delivery.uber_state = new_uber_state
    delivery.save()

    websocket_connections_ids = get_websocket_connections_ids_from_delivery(
        delivery
    )

    dispatch_event(
        {
            "type": "deliveries.delivery.status_updated"
        },
        websocket_connections_ids
    )

    return sanic.empty()
