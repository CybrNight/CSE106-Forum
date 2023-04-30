from . import db
from flask_login import UserMixin
from sqlalchemy import event
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, gen_salt
import uuid
from .enums import Role, TagType
from random import randint
from datetime import datetime


def generate_uuid(model, size=32):
    temp_uuid = uuid.uuid4().hex[:size]
    exists = True

    while exists:
        exists = db.session.query(model.uuid).filter_by(
            uuid=temp_uuid).first() is not None
        temp_uuid = uuid.uuid4().hex[:size]

    return temp_uuid


class PostReply(db.Model):
    __tablename__ = "post_reply"

    id = db.Column(db.Integer, primary_key=True)
    user_uuid = db.Column(db.VARCHAR(255), db.ForeignKey(
        "user.uuid"), nullable=False)
    post_uuid = db.Column(db.VARCHAR(255), db.ForeignKey(
        "post.uuid"), nullable=False)
    reply_uuid = db.Column(
        db.VARCHAR(255), db.ForeignKey("reply.uuid"), nullable=False)

    __table_args__ = (db.UniqueConstraint(user_uuid, post_uuid, reply_uuid),)

    user = db.relationship("User", back_populates="post_replies")
    post = db.relationship("Post", back_populates="post_replies")
    reply = db.relationship("Reply", back_populates="post_replies")

    def get(self):
        return (self.user, self.post, self.reply)


tags = db.Table("post_tags",
                db.Column("tag_id", db.Integer, db.ForeignKey(
                    "tag.id"), primary_key=True),
                db.Column("post_uuid", db.VARCHAR(255), db.ForeignKey(
                    "post.uuid"), primary_key=True)
                )


class User(UserMixin, db.Model):
    # primary keys are required by SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String)
    salt = db.Column(db.VARCHAR(255))
    name = db.Column(db.String(100))
    uuid = db.Column(db.VARCHAR(255), unique=True, nullable=False)
    role = db.Column(db.Enum(Role))
    post_replies = db.relationship(
        "PostReply", back_populates="user", lazy="joined", cascade='all, delete-orphan')
    posts = db.relationship("Post", lazy="subquery",
                            backref=db.backref('user', lazy=True))

    def __repr__(self):
        return self.name

    def __init__(self, name, email="default", password="123", role=Role.DEFAULT):
        self.name = name
        self.email = email
        self.salt = -1
        self.password = password
        self.role = role

        # When a new User object is initialized, set its user uuid to unique value
        self.uuid = generate_uuid(User)

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


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.VARCHAR(255), unique=True, nullable=False)
    title = db.Column(db.String, unique=True)
    author_id = db.Column(db.VARCHAR(255), db.ForeignKey(
        "user.uuid"), nullable=False)
    content = db.Column(db.VARCHAR)
    date = db.Column(db.String)
    upvotes = db.Column(db.Integer)
    downvotes = db.Column(db.Integer)
    tags = db.relationship("Tag", secondary=tags,
                           lazy="subquery", backref=db.backref('posts', lazy=True))

    post_replies = db.relationship(
        "PostReply", back_populates="post", lazy="joined", cascade='all, delete-orphan')

    def __init__(self, title, content=""):
        self.title = title
        self.content = content
        self.date = datetime.now().date().strftime("%d %b %Y")
        self.upvotes = 1
        self.downvotes = 0

        self.uuid = generate_uuid(Post, 8)
        db.session.commit()

    def upvote(self):
        self.upvotes += 1

    def downvote(self):
        self.downvote += 1

    @property
    def total_votes(self):
        return self.upvotes - self.downvotes

    @property
    def tag_list(self):
        tags = []
        for tag in self.tags:
            tags.append({"value": tag.type.value})
        return {"tags": tags}


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(TagType))

    def __init__(self, type):
        self.type = type


class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.VARCHAR(255), nullable=False, unique=True)
    content = db.Column(db.VARCHAR())
    upvotes = db.Column(db.Integer)
    downvotes = db.Column(db.Integer)
    post_replies = db.relationship(
        "PostReply", back_populates="reply", lazy="joined", cascade='all, delete-orphan')

    def __init__(self, content=""):
        self.upvotes = 1
        self.downvotes = 0
        self.content = content
        self.uuid = generate_uuid(Reply, 8)

    def upvote(self):
        self.upvotes += 1

    def downvote(self):
        self.downvote += 1

    @property
    def total_votes(self):
        return self.upvotes - self.downvotes


@ event.listens_for(User.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    if value != oldvalue:
        # When the password is changed, also update the salt
        target.salt = gen_salt(64)
        return generate_password_hash(target.salt+value, method="sha256")
    return value
