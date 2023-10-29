import sanic
from datetime import datetime, timedelta
from models.post import Post
from models.sale import Sale
from models.users import Store, Customer
from utilities.stripe import create_payment_intent
from utilities.event_dispatching import dispatch_event

sales_service = sanic.Blueprint(
    "SalesService",
    url_prefix="/sales_service"
)


def make_sale_json_view(sale):
    post = sale.post.single()
    multimedia_items = [
        item.content_bytes
        for item in post.multimedia_items.all()
    ]

    json = {
        "post": {
            **post.__properties__,
            "multimedia": multimedia_items
        },
        **sale.__properties__
    }

    return json


def get_websocket_connections_ids_from_sale(sale):
    customer = sale.customer.single()
    websocket_connections = customer.websocket_connections.all()

    connections_ids = [
        connection.connection_id
        for connection in websocket_connections
    ]

    return connections_ids


@sales_service.post("/create_sale_intent")
def create_sale_intent(request):
    customer_id = request.json["customer_id"]
    post_id = request.json["post_id"]
    amount = request.json["amount"]

    post = Post.nodes.first(post_id=post_id)
    customer = Customer.nodes.first(user_id=customer_id)
    store = post.store.single()
    payment_intent = create_payment_intent(
        stripe_account_id=store.stripe_account_id,
        price=int(post.price * amount * 100)
    )
    sale = Sale(
        amount=amount,
        stripe_payment_intent_id=payment_intent["id"]
    ).save()

    sale.post.connect(post)
    customer.purchases.connect(sale)
    store.sales.connect(sale)

    post.amount -= amount
    post.save()

    json = {
        "stripe_client_secret": payment_intent.client_secret,
        "sale_id": sale.sale_id
    }

    return sanic.json(json)


@sales_service.post("/get_customer_purchases")
def get_customer_purchases(request):
    customer_id = request.json["customer_id"]

    customer = Customer.nodes.first(user_id=customer_id)
    purchases = customer.purchases.all()

    json = [
        make_sale_json_view(purchase)
        for purchase in purchases
    ]

    return sanic.json(json)


@sales_service.post("/get_customer_undelivered_purchases")
def get_customer_undelivered_purchases(request):
    customer_id = request.json["customer_id"]

    customer = Customer.nodes.first(user_id=customer_id)
    purchases = customer.purchases.all()
    undelivered_purchases = [
        purchase
        for purchase in purchases
        if purchase.delivery.single() is None
    ]

    json = [
        make_sale_json_view(purchase)
        for purchase in undelivered_purchases
    ]

    return sanic.json(json)


@sales_service.post("/get_store_sales")
def get_store_sales(request):
    store_id = request.json["store_id"]

    store = Store.nodes.first(user_id=store_id)
    sales = store.sales.all()

    json = [
        make_sale_json_view(sale)
        for sale in sales
    ]

    return sanic.json(json)


@sales_service.post("/get_store_sales_report")
def get_store_sales_report(request):
    store_id = request.json["store_id"]

    store = Store.nodes.first(user_id=store_id)

    sales_today_amount = len(store.sales.filter(
        purchase_date__gt=datetime.now() - timedelta(hours=24)
    ))
    sales_this_week_amount = len(store.sales.filter(
        purchase_date__gt=datetime.now() - timedelta(days=7)
    ))
    sales_this_month_amount = len(store.sales.filter(
        purchase_date__gt=datetime.now() - timedelta(days=30)
    ))
    sales_this_year_amount = len(store.sales.filter(
        purchase_date__gt=datetime.now() - timedelta(days=365)
    ))

    json = {
        "amount_today": sales_today_amount,
        "amount_this_week": sales_this_week_amount,
        "amount_this_month": sales_this_month_amount,
        "amount_this_year": sales_this_year_amount
    }

    return sanic.json(json)


@sales_service.post("/get_store_sales_chart_data")
def get_store_sales_chart_data(request):
    store_id = request.json["store_id"]

    store = Store.nodes.first(user_id=store_id)
    current_year = datetime.now().year
    current_month = datetime.now().month

    json = []

    for i in range(5):
        sales_amount = len(list(filter(
            lambda s: s.purchase_date.year == current_year and s.purchase_date.month == current_month,
            store.sales.all()
        )))
        month_label = [
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre"
        ][current_month - 1]
        year_label = str(current_year)

        json.append([month_label, year_label, sales_amount])

        if current_month - 1 <= 0:
            current_year -= 1
            current_month = 12
        else:
            current_month -= 1

    return sanic.json(list(reversed(json)))


@sales_service.post("/stripe_payment_intent_status_webhook")
def stripe_payment_intent_status_webhook(request):
    payload = request.json
    payment_intent_id = request.json["data"]["object"]["id"]

    sale = Sale.nodes.first(stripe_payment_intent_id=payment_intent_id)

    websocket_connections_ids = get_websocket_connections_ids_from_sale(
        sale
    )

    match payload["type"]:
        case "payment_intent.succeeded":
            sale.purchase_date = datetime.now()
            sale.save()

            dispatch_event(
                {
                    "type": "sales.payment_intent.succeeded",
                    "sale_id": sale.sale_id
                },
                websocket_connections_ids
            )

        case "payment_intent.failed":
            dispatch_event(
                {
                    "type": "sales.payment_intent.failed"
                },
                websocket_connections_ids
            )
