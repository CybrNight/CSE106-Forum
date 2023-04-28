from http.client import HTTPException
from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import login_required, fresh_login_required, current_user
from . import db
from flask import jsonify
from project.enums import Role
import git

main = Blueprint('main', __name__)

# Route to update the reload the server with latest repo changes if any


@main.route('/reload_server', methods=['POST'])
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
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

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
