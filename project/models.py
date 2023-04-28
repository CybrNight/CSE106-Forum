from . import db
from flask_login import UserMixin
from sqlalchemy import event
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash
import uuid
from .enums import Role, TagType
from random import randint
from datetime import datetime


class Enrollment(db.Model):
    __tablename__ = "enrollment"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "user.user_id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey(
        "course.course_id"), nullable=False)

    __table_args__ = (db.UniqueConstraint(user_id, course_id),)

    user = db.relationship("User", back_populates="enrollment")
    course = db.relationship(
        "Course", back_populates="enrollment")
    grade = db.Column(db.Integer)

    def __repr__(self):
        return f"{self.course}  {self.user}"


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
    enrollment = db.relationship(
        "Enrollment", back_populates="user", lazy="joined", cascade='all, delete-orphan')
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
    date = db.Column(db.DateTime)
    upvotes = db.Column(db.Integer)
    downvotes = db.Column(db.Integer)
    tags = db.relationship("Tag", secondary=tags,
                           lazy="subquery", backref=db.backref('posts', lazy=True))

    post_replies = db.relationship(
        "PostReply", back_populates="post", lazy="joined", cascade='all, delete-orphan')

    def __init__(self, title, content=""):
        self.title = title
        self.content = content
        self.date = datetime.now().date()

        self.upvotes = 1
        self.downvotes = 0

        temp = uuid.uuid4().hex[:8]
        exists = db.session.query(Course.course_id).filter_by(
            course_id=temp).first() is not None

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


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String, unique=True)
    name = db.Column(db.String(100), unique=True)
    time = db.Column(db.String(100))
    enrolled = db.Column(db.Integer)
    max_enroll = db.Column(db.Integer)
    prof_name = db.Column(db.String(100))
    enrollment = db.relationship(
        "Enrollment", back_populates="course", lazy="joined", cascade='all, delete-orphan')

    def __init__(self, name, time, max_enroll=8):
        self.name = name
        self.time = time
        self.enrolled = 0
        self.prof_name = "NULL"
        self.max_enroll = max_enroll

        course_id = uuid.uuid4().hex[:8]
        exists = db.session.query(Course.course_id).filter_by(
            course_id=course_id).first() is not None

        while exists:
            course_id = uuid.uuid4().hex[:8]

        self.course_id = course_id
        db.session.commit()

    def __repr__(self):
        return self.name

    # Update the enroll count
    def set_enroll_count(self):
        enrollment = Enrollment.query.join(Course).join(User).filter(
            (User.role == Role.DEFAULT) & (Course.name == self.name)).all()
        self.enrolled = len(enrollment)

    # Update the professor name
    def set_prof_name(self):
        enrollment = Enrollment.query.join(Course).join(User).filter(
            (User.role == Role.PROFESSOR) & (Course.name == self.name)).all()
        self.prof_name = ""
        for e in enrollment:
            self.prof_name += str(e.user) + "\n"

    def update(self):
        self.set_enroll_count()
        self.set_prof_name()

    # Add user to course enrollment
    def add_user(self, user, grade=-1):
        if grade == -1:
            grade = randint(0, 100)
        if self.enrolled < self.max_enroll:
            db.session.add(Enrollment(user=user, course=self, grade=grade))
            if (user.role == Role.PROFESSOR):
                self.prof_name = user.name
        else:
            raise Exception(f"Class {self} full!")
        self.update()

    # Remove user from course enrollment
    def remove_user(self, user):
        test = Enrollment.query.filter_by(
            course_id=self.course_id, user_id=user.user_id).delete()
        self.update()


@ event.listens_for(User.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    if value != oldvalue:
        return generate_password_hash(value, method="sha256")
    return value
