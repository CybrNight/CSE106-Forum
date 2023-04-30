"""Module provides required Flask utility functions for routes"""
from flask import (Blueprint, flash, redirect, render_template, request,
                   session, url_for)
from flask_login import login_required, login_user, logout_user

from project.util import check_salted_hash
from project import db
from project.models import User

auth = Blueprint('auth', __name__)


@auth.route('/login/', methods=['GET', 'POST'])
def login():
    # Defines Flask route to handle login requests
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        # login code goes here
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()
        salt = user.salt
        hash = user.password

        # Check if the user does not exist or password has does not match
        if not user or not check_salted_hash(hash, password, salt):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))

        # Login user if they pass auth check
        login_user(user, remember=remember)

        # If admin logs in take them straight to admin panel
        if user.is_admin():
            return (redirect("/admin"))

        # Take regular users to the main view
        return redirect(url_for("main.index"))


@auth.route('/signup/', methods=['GET', 'POST'])
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
            return redirect(url_for('auth.signup'))

        # Create new user object, password hashing handled in models.py
        new_user = User(email=email, name=name,
                        password=password)

        # Add user to db
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))


@auth.route('/logout/', methods=['GET'])
@login_required
def logout():
    # Defines Flask route to handle logout requests

    # Clear out session data and logout user
    session.clear()
    logout_user()

    # Redirect user to the homepage
    return redirect(url_for("main.index"))
