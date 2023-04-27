from http.client import HTTPException
from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import login_required, fresh_login_required, current_user
from . import db
from .models import Course, User, Enrollment
from flask import jsonify
from project.enums import Role
import git

post = Blueprint('post', __name__)


@post.route("/testpost", methods=['GET'])
def testpost():
    return render_template("view_post.html")


@post.route("/posts", methods=['GET'])
def get_posts():
    return "Success!", 205


@post.route("/posts/add", methods=['POST'])
def add_post():
    data = request.json

    return "Success!", 205
