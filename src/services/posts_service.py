import sanic
from neomodel import db
from models.post import Post
from models.users import Store, Customer
from models.category import Category
from models.post_multimedia_item import PostMultimediaItem

posts_service = sanic.Blueprint("PostsService", url_prefix="/posts_service")


def create_post_multimedia_items(post, content_bytes_list):
    for content_bytes in content_bytes_list:
        post_multimedia_item = PostMultimediaItem(content_bytes=content_bytes).save()

        post.multimedia_items.connect(post_multimedia_item)


def fetch_categories(categories_names):
    for category_name in categories_names:
        category_or_none = Category.nodes.first_or_none(name=category_name)

        if category_or_none is None:
            category_or_none = Category(name=category_name).save()

        yield category_or_none


def make_post_json_view(post, customer_id):
    store_name = post.store.single().name
    multimedia_items = [
        item.content_bytes
        for item in post.multimedia_items.all()
    ]
    categories = [
        category.name
        for category in post.categories.all()
    ]
    like_count = len(post.liking_customers.all())

    if customer_id is None:
        does_customer_like_post = False
    else:
        customer = Customer.nodes.first(user_id=customer_id)

        does_customer_like_post = customer.liked_posts.is_connected(post)

    json = {
        **post.__properties__,
        "store_name": store_name,
        "multimedia": multimedia_items,
        "categories": categories,
        "likes": like_count,
        "does_customer_like_post": does_customer_like_post
    }

    return json


@posts_service.post("/create_post")
def create_post(request):
    store_id = request.json.pop("store_id")
    categories_names = request.json.pop("categories")
    multimedia_items = request.json.pop("multimedia")

    store = Store.nodes.first(user_id=store_id)
    post = Post(**request.json).save()

    post.store.connect(store)

    categories = fetch_categories(categories_names)

    for category in categories:
        post.categories.connect(category)

    create_post_multimedia_items(post, multimedia_items)

    return sanic.empty()


@posts_service.post("/like_post")
def like_post(request):
    customer_id = request.json["customer_id"]
    post_id = request.json["post_id"]

    post = Post.nodes.first(post_id=post_id)
    customer = Customer.nodes.first(user_id=customer_id)

    post.liking_customers.connect(customer)

    return sanic.empty()


@posts_service.post("/update_post")
def update_post(request):
    post_id = request.json.pop("post_id")
    new_categories_names = request.json.pop("categories")
    new_multimedia_items = request.json.pop("multimedia")

    post = Post.nodes.first(post_id=post_id)

    new_categories = fetch_categories(new_categories_names)

    for new_category in new_categories:
        if not post.categories.is_connected(new_category):
            post.categories.connect(new_category)

    for old_multimedia_item in post.multimedia_items.all():
        old_multimedia_item.delete()

    create_post_multimedia_items(post, new_multimedia_items)

    post.title = request.json["title"]
    post.description = request.json["description"]
    post.price = request.json["price"]
    post.amount = request.json["amount"]

    post.save()

    return sanic.empty()


@posts_service.post("/delete_post")
def delete_post(request):
    post_id = request.json["post_id"]

    post = Post.nodes.first(post_id=post_id)

    for multimedia_item in post.multimedia_items.all():
        multimedia_item.delete()

    for comment in post.comments.all():
        comment.delete()

    post.delete()

    return sanic.empty()


@posts_service.post("/get_post_by_id")
def get_post_by_id(request):
    post_id = request.json["post_id"]

    post = Post.nodes.first(post_id=post_id)
    json = make_post_json_view(post)

    return sanic.json(json)


@posts_service.post("/get_customer_liked_posts")
def get_customer_liked_posts(request):
    customer_id = request.json["customer_id"]

    customer = Customer.nodes.first(user_id=customer_id)
    liked_posts = customer.liked_posts.all()

    json = [
        make_post_json_view(post, customer_id)
        for post in liked_posts
    ]

    return sanic.json(json)


@posts_service.post("/get_store_posts")
def get_store_posts(request):
    store_id = request.json["store_id"]
    customer_id = request.json.get("customer_id")

    store = Store.nodes.first(user_id=store_id)
    posts = store.posts.all()

    json = [
        make_post_json_view(post, customer_id)
        for post in posts
    ]

    return sanic.json(json)


# @posts_service.post("/get_all_posts")
# def get_all_posts(request):
#     """
#     Este endpoint es principalmente para pruebas.
#     En producción no tiene mucho uso.
#     """
# 
#     start = request.json["start"]
#     amount = request.json["amount"]
#     sorting_property = request.json["sort_by"]
# 
#     posts = Post.nodes.order_by(sorting_property)[start:amount]
# 
#     json = [
#         make_post_json_view(post)
#         for post in posts
#     ]
# 
#     return sanic.json(json)


@posts_service.post("/get_posts_from_customer_following_stores")
def get_posts_from_customer_following_stores(request):
    start = request.json["start"]
    amount = request.json["amount"]
    customer_id = request.json["customer_id"]

    query = """
    MATCH (:Customer {user_id: $customer_id})-[:FOLLOWS]-(:Store)-[:POSTED]-(p:Post)
    RETURN DISTINCT p AS posts
    ORDER BY p.publication_date DESC
    SKIP $start
    LIMIT $amount
    """

    result, _ = db.cypher_query(
        query,
        {
            "start": start,
            "amount": amount,
            "customer_id": customer_id
        },
        resolve_objects=True
    )

    json = [
        make_post_json_view(row[0], customer_id)
        for row in result
    ]

    return sanic.json(json)


@posts_service.post("/search_posts_by_metadata")
def search_posts_by_metadata(request):
    start = request.json["start"]
    amount = request.json["amount"]
    searched_text = request.json["searched_text"]
    categories = request.json["categories"]
    sorting_property = request.json["sorting_property"]
    sorting_schema = request.json["sorting_schema"]
    customer_id = request.json.get("customer_id")

    sorting_schema_keyword = (
        "ASC" if sorting_schema.lower() == "ascending" else "DESC"
    )

    query = f"""
    MATCH (p:Post)-[:HAS]->(c:Category)
    WHERE {"c.name IN $categories" if len(categories) > 0 else "TRUE"}
    AND ((p.title CONTAINS $searched_text)
         OR (p.description CONTAINS $searched_text))
    RETURN DISTINCT p AS posts
    ORDER BY $sorting_property {sorting_schema_keyword}
    SKIP $start
    LIMIT $amount
    """

    result, _ = db.cypher_query(
        query,
        {
            "start": start,
            "amount": amount,
            "searched_text": searched_text,
            "categories": categories,
            "sorting_property": sorting_property,
        },
        resolve_objects=True
    )

    json = [
        make_post_json_view(row[0], customer_id)
        for row in result
    ]

    return sanic.json(json)
