from sanic import Blueprint
from sanic import empty
from neomodel import DoesNotExist
from models.category_model import CategoryModel
from models.post_model import PostModel
from models.post_multimedia_model import PostMultimediaModel
from models.comment_model import CommentModel

post_blueprint = Blueprint("PostsBlueprint", url_prefix="/posts")


@post_blueprint.post("/add_comment")
def add_comment(request):
    body = request.json
    text = body["text"]
    post_id = body["post_id"]

    comment = CommentModel(text=text)
    comment.save()

    post = PostModel.nodes.get(id=post_id)
    post.comments.connect(comment)


@post_blueprint.post("/create_post")
def create_post(request):
    body = request.json

    category_names = body["categories"]
    del body["categories"]

    multimedia_list = body["multimedia"]
    del body["multimedia"]

    post = PostModel(**body)
    post.save()

    for category_name in category_names:
        category = None

        try:
            category = CategoryModel.nodes.get(name=category)
        except DoesNotExist:
            category = CategoryModel(name=category_name)
            category.save()

        post.categories.connect(category)

    for multimedia_bytes in multimedia_list:
        post_multimedia = PostMultimediaModel(content_bytes=multimedia_bytes)
        post_multimedia.save()
        post.multimedia.connect(post_multimedia)

    return empty()
