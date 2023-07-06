import sanic
from models.users import Store, Customer

sales_service = sanic.Blueprint(
    "SalesService",
    url_prefix="/sales_service"
)


def make_sale_json_view(sale):
    post = sale.post.single()

    json = {
        **post.__properties__,
        "sale_date": sale.sale_date
    }

    return json


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
