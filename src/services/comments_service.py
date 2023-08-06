import sanic
from models.comment import Comment
from models.users import BaseUser
from models.post import Post
from utilities.users import format_user_name

comments_service = sanic.Blueprint(
    "CommentsService",
    url_prefix="/comments_service"
)


def make_comment_json_view(comment):
    user = comment.user.single()

    json = {
        **comment.__properties__,
        "user_name": format_user_name(user),
        "user_picture": user.picture
    }

    return json


@comments_service.post("/add_comment")
def add_comment(request):
    text = request.json["text"]
    post_id = request.json["post_id"]
    user_id = request.json["user_id"]

    post = Post.nodes.first(post_id=post_id)
    user = BaseUser.nodes.first(user_id=user_id)
    comment = Comment(text=text).save()

    post.comments.connect(comment)
    comment.user.connect(user)

    return sanic.empty()


@comments_service.post("/update_comment")
def update_comment(request):
    comment_id = request.json["comment_id"]

    comment = Comment.nodes.first(comment_id=comment_id)

    comment.text = request.json["text"]
    comment.save()

    return sanic.empty()


@comments_service.post("/delete_comment")
def delete_comment(request):
    comment_id = request.json["comment_id"]

    comment = Comment.nodes.first(comment_id=comment_id)
    comment.delete()

    return sanic.empty()


@comments_service.post("/get_post_comments")
def get_post_comments(request):
    start = request.json["start"]
    amount = request.json["amount"]
    post_id = request.json["post_id"]

    post = Post.nodes.first(post_id=post_id)
    comments = post.comments.all()[start:amount]

    json = [
        make_comment_json_view(comment)
        for comment in comments
    ]

    return sanic.json(json)
