from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from random import randint, choice, shuffle
import requests
import os

from project.enums import Role, TagType

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
lorem = "https://baconipsum.com/api/?type=meat-and-filler"


def create_posts():
    path = os.getcwd()
    path = os.path.join(path, "project/post.txt")

    post_text = ""
    with open(path, 'r') as file:
        post_text = file.read()

    from .models import User, Post, Tag, Reply, PostReply

    posts = {}
    replies = []
    reply_content = ["#PETA FOREVER YOU PEOPLE ARE MURDERERS",
                     "I love meat", "BEEF, It's what's for dinner b*tch"]
    users = User.query.all()

    for i in range(0, 25):
        type = choice(list(TagType))
        posts.update({Post(title=f"Post{i+1}"): Tag(type=type)})

        for j in range(0, 5):
            replies.append(Reply(content=choice(reply_content)))

    for user in users:
        if not len(posts) > 0:
            continue

        post, tag = choice(list(posts.items()))
        del posts[post]
        post.content = post_text
        post.tags.append(tag)
        user.posts.append(post)
        db.session.add_all([post, tag])
        if len(replies) > 0:
            a = randint(2, 4)
            for j in range(1, a):
                shuffle(replies)
                reply = replies.pop()
                reply.content = choice(reply_content)
                db.session.add_all([user, post, reply])
                db.session.add(PostReply(user=user, post=post, reply=reply))
    db.session.commit()


def create_users():
    from .models import User

    # Create user acccounts
    ralph = User(name="Ralph Jenkins", role=Role.DEFAULT)
    susan = User(name="Suan Walker", role=Role.DEFAULT)
    ammon = User(name="Ammon Hepworth", role=Role.DEFAULT)
    jose = User(name="Jose Santos")
    betty = User(name="Betty Brown")
    john = User(name="John Stuart")
    li = User(name="Li Cheng")
    mindy = User(name="Mindy Cheng")
    aditya = User(name="Aditya Ranganath")
    yi = User(name="Yi Wen Chen")
    nancy = User(name="Nancy Little")

    db.session.add_all([ralph, susan, ammon, jose, betty,
                        john,
                        mindy,
                        aditya,
                        yi, nancy])

    db.session.commit()


def create_random_users():
    from .models import User
    users = []
    for i in range(0, 16):
        users.append(User(
            name=f"User{i}", role=Role.DEFAULT))

    db.session.commit()


def create_app():
    app = Flask(__name__,  static_url_path="/static", static_folder="static")

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.session_protection = "strong"
    login_manager.init_app(app)

    from .models import User, Post, Reply
    from .admin import AdminView

    admin = Admin(app, name="Dashboard", index_view=AdminView(
        User, db.session, url='/admin', endpoint='admin'))
    admin.add_view(ModelView(Post, db.session))
    admin.add_view(ModelView(Reply, db.session))

    @ login_manager.user_loader
    def load_user(uuid):
        # since the user uuid is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(uuid))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .post import post as post_blueprint
    app.register_blueprint(post_blueprint)

    return app


def rebuild(random=False):
    from .models import User
    app = create_app()
    app.app_context().push()
    db.drop_all()
    db.create_all()

    if random:
        create_random_users()
    else:
        create_users()

    create_posts()

    db.session.add(User(role=Role.ADMIN, name="ADMIN",
                        email="admin@me.com"))

    db.session.commit()


flask_app = create_app()
