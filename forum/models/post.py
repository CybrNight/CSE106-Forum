from datetime import datetime
from forum import db
from forum.util.hash import gen_model_uuid
from forum.models.enums import TagType, VoteType


class PostVote(db.Model):
    '''Defines an association object linking a User to a up/down vote on a Reply'''
    __tablename__ = "post_vote"

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

    # Define table unique contrains
    __table_args__ = (db.UniqueConstraint(user_uuid, post_uuid),)

    # Define user, post, and reply association
    user = db.relationship("User", back_populates="post_votes")
    post = db.relationship("Post", back_populates="post_votes")
    vote = db.Column(db.Enum(VoteType))

    # Define method to retrieve an entry as a tuple
    def get(self):
        return (self.user, self.post)


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
    title = db.Column(db.String, unique=False)
    uri = db.Column(db.String, unique=False)
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

    post_votes = db.relationship("PostVote",
                                 back_populates="post",
                                 lazy="joined",
                                 cascade='all, delete-orphan')

    def __init__(self, title="NOTHING", content="NOTHING"):
        self.title = title
        self.content = content
        self.date = datetime.now().date().strftime("%d %b %Y")
        self.upvotes = 0
        self.downvotes = 0

        self.uuid = gen_model_uuid(Post, 8)
        self.uri = self.title.replace(" ", "_").lower()
        db.session.commit()

    @property
    def total_votes(self):
        up = 0
        down = 0

        for p_vote in self.post_votes:
            if VoteType(p_vote.vote) == VoteType.UP:
                up += 1
            else:
                down += 1
        self.upvotes = up
        self.downvotes = down
        db.session.commit()
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
