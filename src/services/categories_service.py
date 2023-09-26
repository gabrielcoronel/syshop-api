import sanic
from models.category import Category

categories_service = sanic.Blueprint(
    "CategoriesService",
    url_prefix="/categories_service"
)


@categories_service.post("/search_categories_by_name")
def search_categories_by_name(request):
    searched_name = request.json["search"]

    search_results = Category.nodes.filter(
        name__icontains=searched_name
    )

    json = [
        category.name
        for category in search_results
    ]

    return sanic.json(json)
