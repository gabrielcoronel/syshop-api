import sanic
from models.post import Post
from models.category import Category
from models.post_multimedia_item import PostMultimediaItem
from models.comment import Comment

posts_service = sanic.Blueprint("PostsService", url_prefix="/posts_service")

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


@posts_service.post("/create_post")
def create_post(request):
    category_names = request.json.pop("categories")
    multimedia_items = request.json.pop("multimedia")

    post = Post(**request.json).save()

    for category_name in category_names:
        category = Category.nodes.first_or_none(name=category_name)

        if category is None:
            category = Category(name=category_name).save()

        post.categories.connect(category)

    for multimedia_item in multimedia_items:
        post_multimedia_item = PostMultimediaItem(content_bytes=multimedia_item).save()

        post.multimedia_items.connect(post_multimedia_item)

    return sanic.empty()


@posts_service.post("/delete_post")
def delete_post(request):
    post_id = request.json["post_id"]

    post = Post.nodes.first(post_id=post_id)

    for multimedia_item in posts.multimedia_items.all():
        multimedia_item.delete()

    for comment in posts.comments.all():
        comment.delete()

    post.delete()