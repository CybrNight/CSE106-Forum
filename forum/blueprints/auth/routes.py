"""Module provides required Flask utility functions for routes"""
from flask import (Blueprint, flash, redirect, render_template, request,
                   session, url_for)
from flask_login import login_required, login_user, logout_user

from forum.util.hash import check_salt_hash
from forum import db
from forum.models import User

auth_bp = Blueprint('auth_bp', __name__,
                    template_folder="templates",
                    static_folder="static")


def redirect_dest(fallback):
    dest = request.args.get('next')
    try:
        dest_url = url_for(dest)
    except:
        return redirect(fallback)
    return redirect(dest_url)


@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    # Defines Flask route to handle login requests
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        # login code goes here
        email = request.form.get('email')
        password = request.form.get('password')
        print(request.form.get('next'))
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()
        # Check if the user does not exist or password has does not match
        if not user or not check_salt_hash(user.password, password, user.salt):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth_bp.login', next=request.args.get('next')))

        # Login user if they pass auth check
        login_user(user, remember=remember)

        # If admin logs in take them straight to admin panel
        if user.is_admin():
            return (redirect("/admin"))

        # Take regular users to the main view
        return redirect_dest(fallback=url_for("main_bp.index"))


@auth_bp.route('/signup/', methods=['GET', 'POST'])
def signup():
    # Defines Flask route to handle signup requests

    # If GET request then take user to signup page
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        # Get user input
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        # If user is found, already in db
        user = User.query.filter_by(email=email).first()

        if user:  # Flash error is user already exists
            flash('Email address already exists')
            return redirect(url_for('auth_bp.signup'))

        # Create new user object, password hashing handled in models.py
        new_user = User(email=email, name=name,
                        password=password)

        # Add user to db
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth_bp.login'))


@auth_bp.route('/logout/', methods=['GET'])
@login_required
def logout():
    # Defines Flask route to handle logout requests

    # Clear out session data and logout user
    session.clear()
    logout_user()

    # Redirect user to the homepage
    return redirect(url_for("main_bp.index"))
