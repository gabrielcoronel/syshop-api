import sanic
import boto3
from datauri import DataURI
from os import getenv
from neomodel import db
from models.post import Post
from models.users import Store, Customer
from models.category import Category
from models.post_multimedia_item import PostMultimediaItem
from dotenv import load_dotenv

load_dotenv()

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
    store = post.store.single()
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
        "store_name": store.name,
        "store_id": store.user_id,
        "multimedia": multimedia_items,
        "categories": categories,
        "likes": like_count,
        "does_customer_like_post": does_customer_like_post
    }

    return json


def translate_keyword(keyword):
    session = boto3.session.Session(
        aws_access_key_id=getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=getenv("AWS_SECRET_ACCESS_KEY")
    )
    client = session.client("translate", region_name="us-west-1")

    response = client.translate_text(
        Text=keyword,
        SourceLanguageCode="en",
        TargetLanguageCode="es"
    )

    translated = response["TranslatedText"]

    return translated


def get_image_keywords(image):
    session = boto3.session.Session(
        aws_access_key_id=getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=getenv("AWS_SECRET_ACCESS_KEY")
    )
    client = session.client("rekognition", region_name="us-west-1")

    response = client.detect_labels(
        Image={
            "Bytes": DataURI(f"data:image/jpeg;base64,{image}").data
        },
        Features=["GENERAL_LABELS"]
    )

    keywords = [
        translate_keyword(label["Name"])
        for label in response["Labels"]
    ]

    return keywords


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

    if not post.liking_customers.is_connected(customer):
        post.liking_customers.connect(customer)
    else:
        post.liking_customers.disconnect(customer)

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

    for sale in post.sales.all():
        sale.delete()

    post.delete()

    return sanic.empty()


@posts_service.post("/get_post_by_id")
def get_post_by_id(request):
    post_id = request.json["post_id"]
    customer_id = request.json.get("customer_id")

    post = Post.nodes.first(post_id=post_id)
    json = make_post_json_view(post, customer_id)

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


@posts_service.post("/get_posts_from_customer_following_stores")
def get_posts_from_customer_following_stores(request):
    customer_id = request.json["customer_id"]

    query = """
    MATCH (:Customer {user_id: $customer_id})-[:FOLLOWS]-(:Store)-[:POSTED]-(p:Post)
    WHERE p.amount > 0
    RETURN DISTINCT p AS posts
    ORDER BY p.publication_date DESC
    """

    result, _ = db.cypher_query(
        query,
        {
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
    searched_text = request.json["searched_text"]
    categories = request.json["categories"]
    sorting_property = request.json["sorting_property"]
    sorting_schema = request.json["sorting_schema"]
    minimum_price = request.json["minimum_price"]
    maximum_price = request.json["maximum_price"]
    customer_id = request.json.get("customer_id")

    sorting_schema_keyword = (
        "ASC" if sorting_schema.lower() == "ascending" else "DESC"
    )

    query = f"""
    MATCH (p:Post)-[:HAS]->(c:Category)
    WHERE p.amount > 0
    AND {"c.name IN $categories" if len(categories) > 0 else "TRUE"}
    AND ((toLower(p.title) CONTAINS toLower($searched_text))
         OR (toLower(p.description) CONTAINS toLower($searched_text)))
    AND $minimum_price <= p.price <= $maximum_price
    RETURN DISTINCT p AS posts
    ORDER BY $sorting_property {sorting_schema_keyword}
    """

    result, _ = db.cypher_query(
        query,
        {
            "searched_text": searched_text,
            "categories": categories,
            "sorting_property": sorting_property,
            "minimum_price": minimum_price,
            "maximum_price": maximum_price
        },
        resolve_objects=True
    )

    json = [
        make_post_json_view(row[0], customer_id)
        for row in result
    ]

    return sanic.json(json)


@posts_service.post("/search_posts_by_image")
def search_posts_by_image(request):
    picture = request.json["picture"]
    customer_id = request.json.get("customer_id")

    keywords = get_image_keywords(picture)

    query = f"""
    MATCH (p:Post)
    WHERE p.amount > 0
    AND (
        any(k IN $keywords WHERE toLower(p.title) CONTAINS toLower(k))
        OR any(k IN $keywords WHERE toLower(p.description) CONTAINS toLower(k))
    )
    RETURN p
    """

    result, _ = db.cypher_query(
        query,
        {
            "keywords": keywords
        },
        resolve_objects=True
    )

    posts = [
        make_post_json_view(row[0], None)
        for row in result
    ]

    json = {
        "keywords": keywords,
        "posts": posts
    }

    return sanic.json(json)


@posts_service.post("/get_maximum_price")
def get_maximum_price(request):
    ordered_posts = Post.nodes.order_by("-price")
    maximum_price = ordered_posts[0].price if len(ordered_posts) > 0 else 0

    return sanic.json(maximum_price)
