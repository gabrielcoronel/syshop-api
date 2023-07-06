import sanic
from models.sale import Sale
from models.users import Store, Customer
from models.location import Location
from models.delivery import Delivery

delivery_service = sanic.Blueprint(
    "DeliveryService",
    url_prefix="/delivery_service"
)


def make_delivery_json_view(delivery):
    post = delivery.sale.single().post.single()

    json = {
        **delivery.__properties__,
        **post.__properties__,
        "location": delivery.location.single().name
    }

    return json


def get_deliveries_from_sales(sales):
    deliveries = [
        sale.delivery.single()
        for sale in sales
        if sale.delivery.single() is not None
    ]

    return deliveries


@delivery_service.post("/create_delivery")
def create_delivery(request):
    sale_id = request.json["sale_id"]
    location_id = request.json["location_id"]

    sale = Sale.nodes.first(sale_id=sale_id)
    location = Location.nodes.first(location_id=location_id)
    delivery = Delivery(
        start_ride_datetime=None,
        end_ride_datetime=None
    )

    delivery.sale.connect(sale)
    delivery.location.connect(location)

    return sanic.empty()


@delivery_service.post("/get_store_pending_deliveries")
def get_store_pending_deliveries(request):
    store_id = request.json["store_id"]

    store = Store.nodes.first(user_id=store_id)
    sales = store.sales.all()
    deliveries = get_deliveries_from_sales(sales)
    pending_deliveries = [
        delivery
        for delivery in deliveries
        if delivery.start_ride_datetime is None
    ]

    json = [
        make_delivery_json_view(delivery)
        for delivery in pending_deliveries
    ]

    return sanic.json(json)


@delivery_service.post("/get_customer_pending_deliveries")
def get_customer_pending_deliveries(request):
    customer_id = request.json["customer_id"]

    customer = Customer.nodes.first(user_id=customer_id)
    purchases = customer.purchases.all()
    deliveries = get_deliveries_from_sales(purchases)
    pending_deliveries = [
        delivery
        for delivery in deliveries
        if delivery.start_ride_datetime is None
    ]

    json = [
        make_delivery_json_view(delivery)
        for delivery in pending_deliveries
    ]

    return sanic.json(json)


@delivery_service.post("/get_customer_incoming_deliveries")
def get_customer_incoming_deliveries(request):
    customer_id = request.json["customer_id"]

    customer = Customer.nodes.first(user_id=customer_id)
    purchases = customer.purchases.all()
    deliveries = get_deliveries_from_sales(purchases)
    pending_deliveries = [
        delivery
        for delivery in deliveries
        if delivery.start_ride_datetime is not None
    ]

    json = [
        make_delivery_json_view(delivery)
        for delivery in pending_deliveries
    ]

    return sanic.json(json)
