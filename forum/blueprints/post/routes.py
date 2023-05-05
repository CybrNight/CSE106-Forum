from flask import Blueprint, redirect, render_template, request, url_for
from flask import flash, escape
from flask_login import current_user, login_required
from markupsafe import Markup
from flask import jsonify

from forum.models import Reply, PostReply, Post, PostVote, User, VoteType, TagType, Tag
from forum import db
from random import choice
import json

# Creates a new flask blueprint for this file
post_bp = Blueprint('post_bp', __name__,
                    template_folder="templates",
                    static_folder="static")


@post_bp.route("/testpost/", methods=['GET'])
def testpost():
    '''
    Defines Flask route to return a valid post from db for testing

    Methods: GET
    '''

    # Redirect user to testpost
    return redirect(url_for("post_bp.get_post",
                            p_uuid="testpost",
                            p_title="testpost"))


@post_bp.route("/posts/<p_uuid>/<p_title>/", methods=['GET', 'PUT'])
def get_post(p_uuid, p_title):
    '''
    Defines Flask route to retrieve specific post

    Methods: GET
    '''

    if request.method == 'GET':
        if p_title == "testpost":
            # If testpost is being loaded, then load the first Post in db
            v_up = Post.query.all()[0]
        else:
            # Query post with UUID
            v_up = Post.query.filter_by(uuid=p_uuid).first()

        # If we found the post then retrieve its data
        if v_up:
            user_vote = VoteType.DEFAULT
            replies = []
            # Get each PostReply entry from the post
            for p_vote in v_up.post_votes:
                if p_vote.user == current_user:
                    user_vote = p_vote.vote

            for p_reply in v_up.post_replies:
                # Get the user, and reply information from the PostReply
                user, _, reply = p_reply.get()

                # Store each Reply object data as JSON
                replies.append(
                    {"author": user.name,
                     "content": reply.content,
                     "votes": reply.total_votes})

            # For the queried post, store its metadata and replies data in JSON
            post_data = {"uuid": v_up.uuid,
                         "title": v_up.title,
                         "content": v_up.content,
                         "votes": v_up.total_votes,
                         "userVote": user_vote.value,
                         "tags": v_up.tag_list,
                         "replies": replies}

            # Return post-view template with post_data filled in
            return render_template("post-view.html", data=post_data)

    elif request.method == 'PUT':
        post = Post.query.filter_by(uuid=p_uuid).first()

        if not current_user.is_authenticated:
            return {"votes": post.total_votes}

        data = request.json

        if post:
            # Get the incoming VoteType
            v_type = VoteType(data["vote-type"])

            # Query all upvotes for Post
            v_up = PostVote.query.join(
                User).filter((User.uuid == current_user.uuid) &
                             (PostVote.vote == VoteType.UP) &
                             (Post.uuid == p_uuid)).all()

            # Query all downvotes for Post
            v_down = PostVote.query.join(
                User).filter((User.uuid == current_user.uuid) &
                             (PostVote.vote == VoteType.DOWN) &
                             (Post.uuid == p_uuid)).all()

            # If user is trying to upvote post
            if v_type == VoteType.UP:
                # Check if the user has downvoted the post, and remove the downvote
                if len(v_down) > 0:
                    for v in v_down:
                        db.session.delete(v)
                    db.session.commit()

                # If user has not upvoted the post, then add their vote
                if len(v_up) == 0:
                    db.session.add(PostVote(post=post,
                                            user=current_user, vote=VoteType.UP))
                else:  # If the user has already upvoted then remove their upvote
                    for v in v_up:
                        db.session.delete(v)
                db.session.commit()
            elif v_type == VoteType.DOWN:
                # Check if the user has downvoted the post, and remove the downvote
                if len(v_up) > 0:
                    for v in v_up:
                        db.session.delete(v)
                    db.session.commit()

                if len(v_down) == 0:
                    db.session.add(PostVote(post=post,
                                            user=current_user, vote=VoteType.DOWN))
                else:  # If user has already downvoted, then remove their downvote
                    for v in v_down:
                        db.session.delete(v)

            # Commit all changes made and return new vote count to front-end
            db.session.commit()
            return {"votes": post.total_votes}
    # If post not found, then 404
    return "Post does not exist", 404


@post_bp.route("/posts/<p_uuid>/<p_title>/reply/", methods=['POST'])
def add_post_reply(p_uuid, p_title):
    '''
    Defines Flask route to add a reply to a Post

    Methods: POST
    '''

    # If the user is not authenticated, flash them a warning message
    if not current_user.is_authenticated:
        # Create warning message
        message = Markup('<h1><a href="/login">Login</a> or'
                         '<a href="/signup">Create Account</a> to post '
                         'reply</h1>')

        # Add message to flash list and reload page
        flash(message, 'error')
        return redirect(url_for("post_bp.get_post",
                                p_uuid=p_uuid,
                                p_title=p_title))

    # Get the reply content from the form
    content = request.form.get('reply-content')
    post = Post.query.filter_by(uuid=p_uuid).first()

    # Create new Reply object, and add new PostReply to the database
    reply = Reply(content=content)
    print(post.uuid)
    db.session.add(PostReply(user=current_user, post=post, reply=reply))
    db.session.commit()

    # Reload the page to show new reply
    return redirect(url_for("post_bp.get_post",
                            p_uuid=p_uuid,
                            p_title=p_title))


@post_bp.route('/posts/', methods=['GET'])
def all_posts():
    '''
    Defines Flask route to bring user to posts page

    Methods: GET
    '''

    # Take admin user to the admin page, admin has no courses
    if current_user.is_authenticated and current_user.is_admin():
        return redirect("/admin")
    # Take user to the teacher or student view based on role
    # if current_user.role == Role.PROFESSOR:
    #    return render_template('teacher.html')
    # elif current_user.role == Role.DEFAULT:
    #    return render_template('courses.html')

    # Return all-posts template if user passes checks
    return render_template('all-posts.html')


@post_bp.route('/getPosts/', methods=['PUT'])
def get_posts():
    '''
    Define Flask route to return list of all posts as JSON data to client

    Methods: PUT
    '''

    filter = request.json
    print(filter)

    if request.method == 'PUT':
        posts = Post.query.all()
        posts_data = []
        for post in posts:
            tags = []
            for tag in post.tags:
                tags.append(tag.type.value)

            if(filter["filter"] == "All" or filter["filter"] in tags):
                posts_data.append({"uuid": post.uuid,
                                "title": post.title,
                                "votes": post.total_votes,
                                "author": post.user.name,
                                "date": post.date,
                                "tags": tags})
        return jsonify(posts_data)

    return "Success!", 205


@post_bp.route("/posts/submit", methods=["GET", 'POST'])
# @login_required
def submit_post():
    '''
    Defines Flask route to create a Post

    Methods: POST
    '''
    if request.method == 'POST':
        # Get the reply content from the form
        title = request.form.get("post-title")
        content = request.form.get('post-content')

        # Create new Reply object, and add new PostReply to the database
        post = Post(title=title, content=content)
        tag = Tag(choice(list(TagType)))
        post.tags.append(tag)
        current_user.posts.append(post)

        db.session.add_all([post, tag])
        db.session.commit()

        # Reload the page to show new reply
        return redirect(url_for("post_bp.get_post",
                                p_uuid=post.uuid,
                                p_title=post.title))
    elif request.method == 'GET':
        return render_template("post-create.html")
