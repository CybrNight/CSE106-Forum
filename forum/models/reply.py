from datetime import datetime
from forum import db
from forum.util.hash import gen_model_uuid
from .enums import TagType, VoteType
from .user import User


class ReplyVote(db.Model):
    '''Defines an association object linking a User to a up/down vote on a Reply'''
    __tablename__ = "reply_vote"

    id = db.Column(db.Integer,
                   primary_key=True)

    # Define user_uuid ForeignKey column
    user_uuid = db.Column(db.VARCHAR(255),
                          db.ForeignKey("user.uuid"),
                          nullable=False)

    # Define post_uuid ForeignKey column
    reply_uuid = db.Column(db.VARCHAR(255),
                           db.ForeignKey("reply.uuid"),
                           nullable=False)

    # Define table unique contrains
    __table_args__ = (db.UniqueConstraint(user_uuid, reply_uuid),)

    # Define user, post, and reply association
    user = db.relationship("User", back_populates="reply_votes")
    reply = db.relationship("Reply", back_populates="reply_votes")
    vote = db.Column(db.Enum(VoteType))

    # Define method to retrieve an entry as a tuple
    def get(self):
        return (self.user, self.post)


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
                          db.ForeignKey("post.id"),
                          nullable=False)

    # Define reply_uuid ForeignKey column
    reply_uuid = db.Column(db.VARCHAR(255),
                           db.ForeignKey("reply.id"),
                           nullable=False)

    # Define table unique contrains
    __table_args__ = (db.UniqueConstraint(user_uuid, post_uuid, reply_uuid),)

    # Define user, post, and reply association
    user = db.relationship("User", back_populates="post_replies")
    post = db.relationship("Post", back_populates="post_replies")
    reply = db.relationship("Reply", back_populates="post_replies")

    def __repr__(self):
        return (self.user.name)

    # Define method to retrieve an entry as a tuple
    def get(self):
        return (self.user, self.post, self.reply)


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

    # Create relationship between Reply and ReplyVote
    reply_votes = db.relationship("ReplyVote",
                                  back_populates="reply",
                                  lazy="joined",
                                  cascade='all, delete-orphan')

    def __init__(self, content=""):
        self.upvotes = 1
        self.downvotes = 0
        self.content = content
        self.uuid = gen_model_uuid(Reply, 8)

    @property
    def total_votes(self):
        up = 0
        down = 0

        for p_vote in self.reply_votes:
            if VoteType(p_vote.vote) == VoteType.UP:
                up += 1
            else:
                down += 1
        self.upvotes = up
        self.downvotes = down
        db.session.commit()
        return self.upvotes - self.downvotes
