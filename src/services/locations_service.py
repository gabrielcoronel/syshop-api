import sanic
from models.location import Location
from models.users import Customer

locations_service = sanic.Blueprint(
    "LocationsService",
    url_prefix="locations_service"
)


@locations_service.post("/add_location")
def add_location(request):
    customer_id = request.json.pop("customer_id")

    customer = Customer.nodes.first(user_id=customer_id)
    location = Location(**request.json).save()

    location.customer.connect(customer)

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


@locations_service.post("/remove_location")
def remove_location(request):
    location_id = request.json["location_id"]

    location = Location.nodes.first(location_id=location_id)
    location.delete()

    return sanic.empty()


@locations_service.post("/update_location")
def update_location(request):
    location_id = request.json["location_id"]

    location = Location.nodes.first(location_id=location_id)

    location.name = request.json["name"]
    location.longitude = request.json["longitude"]
    location.latitude = request.json["latitude"]

    location.save()

    return sanic.empty()
