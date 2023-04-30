from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from forum.util import rebuild_db
import sys

sys.dont_write_bytecode = True

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()


def create_app():
    app = Flask(__name__,
                template_folder="./templates",
                static_url_path="/static",
                static_folder="./static")

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth_bp.login'
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
    from .blueprints import auth_bp, main_bp, post_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(post_bp)

    return app


def run_app(debug, rebuild=False):
    if rebuild:
        rebuild_db(test_data=debug)
    flask_app.run(debug=debug)


flask_app = create_app()
