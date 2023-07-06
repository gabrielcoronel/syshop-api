import sanic
from models.category import Category

categories_service = sanic.Blueprint(
    "CategoriesService",
    url="/categories_service"
)


@categories_service.post("/search_categories_by_name")
def search_categories_by_name(request):
    start = request.json["start"]
    amount = request.json["amount"]
    searched_name = request.json["search"]

    search_results = Category.nodes.filter(
        name__icontains=searched_name
    )[start:amount]

    json = [
        category.name
        for category in search_results
    ]

    return sanic.json(json)
