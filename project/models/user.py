from flask_login import UserMixin
from sqlalchemy import event
from project import db
from project.util import generate_salted_hash, generate_uuid
from werkzeug.security import gen_salt
from project.enums import Role


class User(UserMixin, db.Model):
    '''Defines User db model to be used by all users'''
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String)
    salt = db.Column(db.VARCHAR(255))
    name = db.Column(db.String(100))
    uuid = db.Column(db.VARCHAR(255), unique=True, nullable=False)
    role = db.Column(db.Enum(Role))
    post_replies = db.relationship("PostReply",
                                   back_populates="user",
                                   lazy="joined",
                                   cascade='all, delete-orphan')
    posts = db.relationship("Post",
                            lazy="subquery",
                            backref=db.backref('user', lazy=True))

    def __repr__(self):
        return self.name

    def __init__(self, name, email="default", password="123",
                 role=Role.DEFAULT):

        self.name = name
        self.email = email
        self.salt = -1
        self.password = password
        self.role = role

        # When a new User object is initialized, set UUID
        self.uuid = generate_uuid(db, User)

        # Set email to generic template based on first+last name
        if self.email == "default":
            names = name.split(" ")

            if len(names) >= 2:
                self.email = (names[0][0] + names[1]).lower()
            else:
                self.email = self.name.lower()
            self.email += "@me.com"

    def is_admin(self):
        return self.role == Role.ADMIN


@ event.listens_for(User.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    # If password has been changed, then update salt and re-hash
    if value != oldvalue:
        target.salt = gen_salt(32)
        return generate_salted_hash(value, target.salt)
    return value
