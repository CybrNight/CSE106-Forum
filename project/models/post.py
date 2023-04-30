from sqlalchemy import event
from datetime import datetime
from project import db
from enum import Enum
from project.util import generate_salted_hash, generate_uuid


class TagType(Enum):
    '''Defines Enum of tags to be used by Post model'''
    SCIENCE = 'Science'
    MATH = 'Math'
    PROGRAMMING = 'Programming'
    HISTORY = 'History'

    def __repr__(self) -> str:
        return self.value


class PostReply(db.Model):
    '''Defines an association object linking a User to a Reply on a Post'''
    __tablename__ = "post_reply"

    id = db.Column(db.Integer,
                   primary_key=True)

    # Define user_uuid ForeignKey column
    user_uuid = db.Column(db.VARCHAR(255),
                          db.ForeignKey("user.uuid"),
                          nullable=False)

    # Define post_uuid ForeignKey column
    post_uuid = db.Column(db.VARCHAR(255),
                          db.ForeignKey("post.uuid"),
                          nullable=False)

    # Define reply_uuid ForeignKey column
    reply_uuid = db.Column(db.VARCHAR(255),
                           db.ForeignKey("reply.uuid"),
                           nullable=False)

    # Define table unique contrains
    __table_args__ = (db.UniqueConstraint(user_uuid, post_uuid, reply_uuid),)

    # Define user, post, and reply association
    user = db.relationship("User", back_populates="post_replies")
    post = db.relationship("Post", back_populates="post_replies")
    reply = db.relationship("Reply", back_populates="post_replies")

    # Define method to retrieve an entry as a tuple
    def get(self):
        return (self.user, self.post, self.reply)


# Define many-to-many assocation table linking a Post to a Tag
post_tags = db.Table("post_tags",
                     db.Column("tag_id", db.Integer, db.ForeignKey(
                         "tag.id"), primary_key=True),
                     db.Column("post_uuid", db.VARCHAR(255), db.ForeignKey(
                         "post.uuid"), primary_key=True)
                     )


class Post(db.Model):
    '''Defines Post db model for storing posts in db'''

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.VARCHAR(255), unique=True, nullable=False)
    title = db.Column(db.String, unique=True)
    author_id = db.Column(db.VARCHAR(255), db.ForeignKey(
        "user.uuid"), nullable=False)
    content = db.Column(db.VARCHAR)
    date = db.Column(db.String)
    upvotes = db.Column(db.Integer)
    downvotes = db.Column(db.Integer)
    tags = db.relationship("Tag", secondary=post_tags,
                           lazy="subquery",
                           backref=db.backref('posts', lazy=True))

    post_replies = db.relationship("PostReply",
                                   back_populates="post",
                                   lazy="joined",
                                   cascade='all, delete-orphan')

    def __init__(self, title, content=""):
        self.title = title
        self.content = content
        self.date = datetime.now().date().strftime("%d %b %Y")
        self.upvotes = 1
        self.downvotes = 0

        self.uuid = generate_uuid(db, Post, 8)
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
    post_replies = db.relationship("PostReply",
                                   back_populates="reply",
                                   lazy="joined",
                                   cascade='all, delete-orphan')

    def __init__(self, content=""):
        self.upvotes = 1
        self.downvotes = 0
        self.content = content
        self.uuid = generate_uuid(db, Reply, 8)

    def upvote(self):
        self.upvotes += 1

    def downvote(self):
        self.downvote += 1

    @property
    def total_votes(self):
        return self.upvotes - self.downvotes
