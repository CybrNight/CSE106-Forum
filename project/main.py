from http.client import HTTPException
from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import login_required, fresh_login_required, current_user
from . import db
from flask import jsonify
from project.enums import Role
import git
from .models import Post, PostReply, Tag, Reply


main = Blueprint('main', __name__)

# Route to update the reload the server with latest repo changes if any


@main.route('/reload_server/', methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('./CSE106-Forum')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400

# Main view


@ main.route('/')
def index():
    return render_template('index.html')


# 404 errors
@ main.app_errorhandler(404)
def page_not_found(e):
    print(e)
    return render_template('error/404.html'), 404


# 403 errors
@ main.app_errorhandler(403)
def forbidden(e):
    print(e)
    return render_template('error/403.html'), 403


@ main.route('/profile/', methods=['GET'])
@login_required
def profile():
    # Take admin user to the admin page, admin has no courses
    if current_user.is_admin():
        return redirect("/admin/")

    # Take user to the teacher or student view based on role
    if current_user.role == Role.PROFESSOR:
        return render_template('teacher.html')
    elif current_user.role == Role.DEFAULT:
        post = Post.query.filter(Post.user == current_user).all()
        posts = []
        for p in post:
            posts.append({"title": p.title,
                          "content": p.content,
                          "upvotes": p.upvotes,
                          "downvotes": p.downvotes})

        print(posts)
        return render_template('profile.html', data=posts)
    # Anyone else gets index
    return render_template('index.html')
