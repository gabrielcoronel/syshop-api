import sanic
from models.post import Post
from models.category import Category
from models.post_multimedia_item import PostMultimediaItem
from models.comment import Comment

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


def make_post_json_view(post):
    multimedia_items = [
        item.content_bytes
        for item in post.multimedia_items.all()
    ]
    categories = [
        category.name
        for category in post.categories.all()
    ]
    comments = [
        comment.__properties__
        for comment in post.comments.all()
    ]

    json = {
        **post.__properties__,
        "multimedia": multimedia_items,
        "categories": categories,
        "comments": comments
    }

    return json


@posts_service.post("/add_comment")
def add_comment(request):
    text = request.json["text"]
    post_id = request.json["post_id"]

    comment = Comment(text=text).save()

    post = Post.nodes.first(post_id=post_id)
    post.comments.connect(comment)

    return sanic.empty()


@posts_service.post("/delete_comment")
def delete_comment(request):
    comment_id = request.json["comment_id"]

    comment = Comment.nodes.first(comment_id=comment_id)
    comment.delete()

    return sanic.empty()


@posts_service.post("/create_post")
def create_post(request):
    categories_names = request.json.pop("categories")
    multimedia_items = request.json.pop("multimedia")

    post = Post(**request.json).save()

    categories = fetch_categories(categories_names)

    for category in categories:
        post.categories.connect(category)

    create_post_multimedia_items(post, multimedia_items)

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


@posts_service.post("/get_all_posts")
def get_all_posts(request):
    start = request.json["start"]
    amount = request.json["amount"]
    sorting_property = request.json["sort_by"]

    posts = Post.nodes.order_by(sorting_property)[start:amount]

    json = [
        make_post_json_view(post)
        for post in posts
    ]

    return sanic.json(json)
