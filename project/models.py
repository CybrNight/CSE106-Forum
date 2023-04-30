from . import db
from flask_login import UserMixin
from sqlalchemy import event
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash
import uuid
from .enums import Role, TagType
from random import randint
from datetime import datetime


class PostReply(db.Model):
    __tablename__ = "post_reply"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    reply_id = db.Column(db.Integer, db.ForeignKey("reply.id"), nullable=False)

    __table_args__ = (db.UniqueConstraint(user_id, post_id, reply_id),)

    user = db.relationship("User", back_populates="post_replies")
    post = db.relationship("Post", back_populates="post_replies")
    reply = db.relationship("Reply", back_populates="post_replies")

    def get(self):
        return (self.user, self.post, self.reply)


tags = db.Table("post_tags",
                db.Column("tag_id", db.Integer, db.ForeignKey(
                    "tag.id"), primary_key=True),
                db.Column("post_id", db.Integer, db.ForeignKey(
                    "post.id"), primary_key=True)
                )


class User(UserMixin, db.Model):
    # primary keys are required by SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    user_id = db.Column(db.String, unique=True)
    role = db.Column(db.Enum(Role))
    post_replies = db.relationship(
        "PostReply", back_populates="user", lazy="joined", cascade='all, delete-orphan')
    posts = db.relationship("Post", lazy="subquery",
                            backref=db.backref('user', lazy=True))

    def is_admin(self):
        return self.role == Role.ADMIN

    def __repr__(self):
        return self.name

    def __init__(self, name, email="default", password="123", role=Role.DEFAULT):
        self.name = name
        self.email = email
        self.password = password
        self.role = role

        # When a new User object is initialized, set its user_id to unique value
        user_id = uuid.uuid4().hex[:8]
        exists = db.session.query(User.user_id).filter_by(
            user_id=user_id).first() is not None

        while exists:
            user_id = uuid.uuid4().hex[:8]

        self.user_id = user_id

        # Set email to generic template based on first+last name
        if self.email == "default":
            names = name.split(" ")

            if len(names) >= 2:
                self.email = (names[0][0] + names[1]).lower()
            else:
                self.email = self.name.lower()
            self.email += "@me.com"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, unique=True)
    title = db.Column(db.String, unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
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

        temp = uuid.uuid4().hex[:8]
        exists = db.session.query(Post.uuid).filter_by(
            uuid=temp).first() is not None

        while exists:
            temp = uuid.uuid4().hex[:8]

        self.uuid = temp
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
    content = db.Column(db.VARCHAR())
    upvotes = db.Column(db.Integer)
    downvotes = db.Column(db.Integer)
    post_replies = db.relationship(
        "PostReply", back_populates="reply", lazy="joined", cascade='all, delete-orphan')

    def __init__(self, content=""):
        self.upvotes = 1
        self.downvotes = 0
        self.content = content

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
        return generate_password_hash(value, method="sha256")
    return value
