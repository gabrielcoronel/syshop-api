from sanic import Blueprint
from sanic import empty
from neomodel import DoesNotExist
from models.category_model import CategoryModel
from models.post_model import PostModel
from models.post_multimedia_model import PostMultimediaModel
from models.comment_model import CommentModel

posts_blueprint = Blueprint("PostsBlueprint", url_prefix="/posts")


@posts_blueprint.post("/add_comment")
def add_comment(request):
    text = request.json["text"]
    post_id = request.json["post_id"]

    comment = CommentModel(text=text).save()

    post = PostModel.nodes.first(post_id=post_id)
    post.comments.connect(comment)

    return empty()


@posts_blueprint.post("/create_post")
def create_post(request):
    category_names = request.json.pop("categories")
    multimedia_items = request.json.pop("multimedia")

    print(request.json)

    post = PostModel(**request.json).save()

    for category_name in category_names:
        category = CategoryModel.nodes.first_or_none(name=category_name)

        if category is None:
            category = CategoryModel(name=category_name).save()

        post.categories.connect(category)

    for multimedia_item in multimedia_items:
        post_multimedia = PostMultimediaModel(content_bytes=multimedia_item).save()

        post.multimedia.connect(post_multimedia)

    return empty()