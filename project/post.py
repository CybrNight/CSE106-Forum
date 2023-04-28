from http.client import HTTPException
from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask import flash
from flask_login import login_required, fresh_login_required, current_user
from markupsafe import Markup
from . import db
from .models import Post, PostReply, User, Reply
from flask import jsonify
from project.enums import Role
import git

post = Blueprint('post_route', __name__)


@post.route("/testpost", methods=['GET'])
def testpost():
    return redirect(url_for("post_route.get_post", p_title="testpost"))


@post.route("/posts/<p_title>", methods=['GET'])
def get_post(p_title):
    if request.method == 'GET':
        # Query join of Post and PostReply to get post with title and its replies

        if p_title == "testpost":
            post = Post.query.all()[0]
        else:
            post = Post.query.join(PostReply).filter(
                Post.title == p_title).first()

        if post:
            replies = []
            for p_reply in post.post_replies:
                user, _, reply = p_reply.get()
                replies.append(
                    {"author": user.name, "content": reply.content, "upvotes": reply.total_votes})
            post_data = {"title": post.title,
                         "content": post.content,
                         "upvotes": post.total_votes,
                         "replies": replies,
                         "tags": post.tag_list}
            print(post_data)
            return render_template("post-view.html", data=post_data)

    return "Post does not exist", 404


@post.route("/posts/<p_title>/reply", methods=['POST'])
def add_post_reply(p_title):
    if not current_user.is_authenticated:
        message = Markup(
            '<h1>You must <a href="/login">login</a> in order to reply</h1>')
        flash(message, 'error')
        return redirect(url_for("post_route.get_post", p_title=p_title))

    content = request.form.get('reply-content')
    post = Post.query.join(PostReply).filter(Post.title == p_title).first()

    reply = Reply(content=content)

    db.session.add(PostReply(user=current_user, post=post, reply=reply))
    db.session.commit()

    return redirect(url_for("post_route.get_post", p_title=p_title))


@ post.route("/posts", methods=['GET'])
def get_posts():
    return "Success!", 205


@ post.route("/posts/add", methods=['POST'])
def add_post():
    data = request.json

    return "Success!", 205
