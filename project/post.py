from http.client import HTTPException
from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import login_required, fresh_login_required, current_user
from . import db
from .models import Post, User, Reply
from flask import jsonify
from project.enums import Role
import git

post = Blueprint('post', __name__)


@post.route("/testpost", methods=['GET'])
def testpost():
    return redirect(url_for("post.get_post", title="Post1"))


@post.route("/posts/<title>", methods=['GET', 'POST'])
def get_post(title):
    if request.method == 'GET':
        post = Post.query.filter_by(title=title).first()

        if post:
            post_data = {"title": post.title, "content": post.content}
            return render_template("view_post.html", data=post_data)

    return "Post does not exist", 404


@ post.route("/posts", methods=['GET'])
def get_posts():
    return "Success!", 205


@ post.route("/posts/add", methods=['POST'])
def add_post():
    data = request.json

    return "Success!", 205
