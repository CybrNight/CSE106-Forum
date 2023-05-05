from forum.models import Post
from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required, current_user
import git

main_bp = Blueprint('main_bp', __name__,
                    template_folder="templates",
                    static_folder="static")


@main_bp.route('/reload_server/', methods=['POST'])
def webhook():
    # Defines webhook for GitHub connection. Auto pull repo changes on server
    if request.method == 'POST':
        repo = git.Repo('./CSE106-Forum')
        origin = repo.remotes.origin
        origin.pull()
        return 'Pulled changes from GitHub to server!', 200
    else:
        return 'Wrong event type', 400


@main_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for("post_bp.all_posts"))


# 404 errors


@ main_bp.app_errorhandler(404)
def page_not_found(e):
    print(e)
    return render_template('error/404.html'), 404


# 403 errors
@ main_bp.app_errorhandler(403)
def forbidden(e):
    print(e)
    return render_template('error/403.html'), 403


@ main_bp.route('/profile/', methods=['GET'])
@login_required
def profile():

    # Defines route for profile view

    # If admin accesses portal then take them to admin panel
    if current_user.is_admin():
        return redirect("/admin/")

    # Query the all posts belonging to user
    post = Post.query.filter(Post.user == current_user).all()
    posts = []
    # For every post in query, add to JSON to send to template
    for p in post:
        posts.append({"title": p.title,
                      "uri": p.uri,
                      "uuid": p.uuid,
                      "content": p.content,
                      "upvotes": p.upvotes,
                      "downvotes": p.downvotes})

    return render_template('profile.html', data=posts)
