from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from random import randint, choice, shuffle
from .enums import Role, TagType
import os

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()


def create_posts():
    from .models import User, Post, Tag, Reply, PostReply
    from project.enums import TagType
    '''
    Creates a set number of random posts when rebuilding the database
    '''
    path = os.getcwd()
    path = os.path.join(path, "project/resources/post.txt")

    post_text = ""
    with open(path, 'r') as file:
        post_text = file.read()

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
    '''Creates default users for testing'''

    from .models import User
    from .enums import Role

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
                        yi, li, nancy])

    db.session.commit()


def create_app():
    app = Flask(__name__,
                template_folder="./resources/templates",
                static_url_path="/static",
                static_folder="./resources/static")

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.session_protection = "strong"
    login_manager.init_app(app)

    from .views import UserView
    from .models import Post, Reply, User

    admin = Admin(app, name="Dashboard", index_view=UserView(
        User, db.session, url='/admin', endpoint='admin'))
    admin.add_view(ModelView(Post, db.session))
    admin.add_view(ModelView(Reply, db.session))

    @ login_manager.user_loader
    def load_user(uuid):
        # Since the User uuid is the primary key User table
        # use it in the query for the User
        return User.query.get(int(uuid))

    # Import and register blueprints
    from project.blueprints import auth_bp, main_bp, post_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(post_bp)

    return app


def rebuild():
    from .models import User

    # Create new app object
    app = create_app()
    app.app_context().push()

    # Re-build all tables
    db.drop_all()
    db.create_all()

    # Generate user accounts
    create_users()

    # Generate default test posts
    create_posts()

    # Add default admin account
    db.session.add(User(role=Role.ADMIN, name="ADMIN",
                        email="admin@me.com"))

    db.session.commit()


flask_app = create_app()
