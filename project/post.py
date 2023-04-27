from http.client import HTTPException
from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import login_required, fresh_login_required, current_user
from . import db
from .models import Post, PostReply, User, Reply
from flask import jsonify
from project.enums import Role
import git

post = Blueprint('post_route', __name__)


@post.route("/testpost", methods=['GET'])
def testpost():
    return redirect(url_for("post.get_post", title="Post1"))


@post.route("/posts/<p_title>", methods=['GET', 'POST'])
def get_post(p_title):
    if request.method == 'GET':
        # Query join of Post and PostReply to get post with title and its replies
        post = Post.query.join(PostReply).filter(Post.title == p_title).first()

        if post:
            replies = []
            for p_reply in post.post_replies:
                user, _, reply = p_reply.get()
                replies.append({"author": user.name, "content": reply.content})
            post_data = {"title": post.title,
                         "content": post.content,
                         "upvotes": post.upvotes,
                         "downvotes": post.downvotes,
                         "replies": replies}
            return render_template("post-view.html", data=post_data)

    return "Post does not exist", 404


@ post.route("/posts", methods=['GET'])
def get_posts():
    return "Success!", 205


@ post.route("/posts/add", methods=['POST'])
def add_post():
    data = request.json

    return "Success!", 205
