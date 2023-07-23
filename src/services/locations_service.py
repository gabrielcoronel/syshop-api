import sanic
from models.location import Location
from models.users import Store, Customer

locations_service = sanic.Blueprint(
    "LocationsService",
    url_prefix="locations_service"
)


@locations_service.post("/add_customer_location")
def add_customer_location(request):
    customer_id = request.json.pop("customer_id")

    customer = Customer.nodes.first(user_id=customer_id)
    location = Location(**request.json).save()

    location.user.connect(customer)

    return sanic.empty()


@locations_service.post("/get_customer_locations")
def get_customer_locations(request):
    customer_id = request.json["customer_id"]

    customer = Customer.nodes.first(user_id=customer_id)
    locations = customer.locations.all()

    json = [
        location.__properties__
        for location in locations
    ]

    return sanic.json(json)


@locations_service.post("/remove_customer_location")
def remove_customer_location(request):
    location_id = request.json["location_id"]

    location = Location.nodes.first(location_id=location_id)
    location.delete()

    return sanic.empty()


@locations_service.post("/update_customer_location")
def update_customer_location(request):
    location_id = request.json["location_id"]

    location = Location.nodes.first(location_id=location_id)

    location.place_name = request.json["place_name"]
    location.street_address = request.json["street_address"]
    location.city = request.json["city"]
    location.state = request.json["state"]
    location.zip_code = request.json["zip_code"]

    location.save()

    return sanic.empty()


@locations_service.post("/get_store_location")
def get_store_location(request):
    store_id = request.json["store_id"]

    store = Store.nodes.first(user_id=store_id)
    location = store.location.single()

    json = location.__properties__

    return sanic.json(json)


@locations_service.post("/update_store_location")
def update_store_location(request):
    store_id = request.json.pop("store_id")

    store = Store.nodes.first(user_id=store_id)
    location = store.location.single()

    location.place_name = request.json["place_name"]
    location.street_address = request.json["street_address"]
    location.city = request.json["city"]
    location.state = request.json["state"]
    location.zip_code = request.json["zip_code"]

    location.save()

    return sanic.empty()
