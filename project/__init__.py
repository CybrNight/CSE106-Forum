from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from random import randint

from project.role import Role

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()


def create_users():
    from .models import User, Course, Enrollment
    profs = []
    courses = []

    math = Course(name="Math 101", time="MWF 10:00-10:50 AM", max_enroll=8)
    phys = Course(name="Physics 121", time="MWF 10:00-10:50 AM", max_enroll=8)
    cs106 = Course(name="CS 106", time="MWF 10:00-10:50 AM", max_enroll=8)
    cs162 = Course(name="CS 162", time="MWF 10:00-10:50 AM", max_enroll=8)

    # Create Professor Accounts
    ralph = User(name="Ralph Jenkins", role=Role.PROFESSOR)
    susan = User(name="Suan Walker", role=Role.PROFESSOR)
    ammon = User(name="Ammon Hepworth", role=Role.PROFESSOR)

    # Create student accounts
    jose = User(name="Jose Santos")
    betty = User(name="Betty Brown")
    john = User(name="John Stuart")
    li = User(name="Li Cheng")
    mindy = User(name="Mindy Cheng")
    aditya = User(name="Aditya Ranganath")
    yi = User(name="Yi Wen Chen")
    nancy = User(name="Nancy Little")

    # Add Professor accounts to courses
    math.add_user(ralph)
    phys.add_user(susan)
    cs106.add_user(ammon)
    cs162.add_user(ammon)

    # Add Student accounts to courses
    math.add_user(jose, grade=92)
    math.add_user(betty, grade=65)
    math.add_user(john, grade=86)
    math.add_user(li, grade=77)

    phys.add_user(nancy, grade=53)
    phys.add_user(li, grade=85)
    phys.add_user(mindy, grade=94)
    phys.add_user(john, grade=91)
    phys.add_user(betty, grade=88)

    cs106.add_user(aditya, grade=93)
    cs106.add_user(yi, grade=85)
    cs106.add_user(nancy, grade=57)
    cs106.add_user(mindy, grade=68)

    cs162.add_user(aditya, grade=99)
    cs162.add_user(nancy, grade=87)
    cs162.add_user(yi, grade=92)
    cs162.add_user(john, grade=67)

    db.session.commit()


def create_random_users():
    from .models import User, Course, Enrollment

    profs = []
    users = []
    courses = []

    for i in range(0, 8):
        courses.append(
            Course(name=f"CSE{100+(i*5)}", time="MWF 10:00-10:50AM", max_enroll=8))
        profs.append(
            User(name=f"Professor{i}", email=f"prof{i}@me.com", role=Role.PROFESSOR))

    for i in range(0, 16):
        users.append(User(
            name=f"Student{i}", role=Role.STUDENT))

    for i in range(1, len(profs)-1):
        db.session.add(courses[i])
        courses[i].add_user(profs[i-1])

        if randint(0, 25) < 10:
            courses[i].add_user(profs[i], )
        for user in users:
            db.session.add(user)

            if randint(0, 25) < 10:
                try:
                    courses[i].add_user(user)
                except Exception as e:
                    print(e)
    db.session.commit()


def create_app():
    app = Flask(__name__,  static_url_path="/static", static_folder="static")

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.session_protection = "strong"
    login_manager.init_app(app)

    from .models import User, Course, Enrollment
    from .admin import AdminView, CourseView

    admin = Admin(app, name="Dashboard", index_view=AdminView(
        User, db.session, url='/admin', endpoint='admin'))
    admin.add_view(CourseView(Course, db.session))

    @ login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app


def rebuild(random=False):
    from .models import User, Course, Enrollment
    app = create_app()
    app.app_context().push()
    db.drop_all()
    db.create_all()

    if random:
        create_random_users()
    else:
        create_users()

    db.session.add(User(role=Role.ADMIN, name="ADMIN",
                        email="admin@me.com"))

    db.session.commit()
