from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask import flash, escape
from flask_login import current_user, login_required
from markupsafe import Markup
from flask import jsonify

from forum.models import (Reply, PostReply, Post,
                          PostVote, VoteType, TagType, Tag, ReplyVote)
from forum import db
from random import choice
import bleach

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
                            p_uri="testpost"))


@post_bp.route("/posts/<p_uuid>/<p_uri>/", methods=['GET', 'PUT'])
def get_post(p_uuid, p_uri):
    '''
    Defines Flask route to retrieve specific post

    Methods: GET
    '''

    if request.method == 'GET':
        if p_uri == "testpost":
            # If testpost is being loaded, then load the first Post in db
            post = Post.query.all()[0]
        else:
            # Query post with UUID
            post = Post.query.filter_by(uuid=p_uuid, uri=p_uri).first()

        # If we found the post then retrieve its data
        if post:
            user_vote = VoteType.NONE
            replies = []
            # Get each PostReply entry from the post
            for p_vote in post.post_votes:
                if p_vote.user == current_user:
                    user_vote = p_vote.vote

            for p_reply in post.post_replies:
                # Get the user, and reply information from the PostReply
                user, _, reply = p_reply.get()

                vote_type = VoteType.NONE
                for r_vote in reply.reply_votes:
                    if r_vote.user == current_user:
                        vote_type = r_vote.vote

                # Store each Reply object data as JSON
                replies.append(
                    {"uuid": reply.uuid,
                     "a_uuid": user.uuid,
                     "author": user.name,
                     "voteType": vote_type.value,
                     "content": reply.content,
                     "votes": reply.total_votes})

            # For the queried post, store its metadata and replies data in JSON
            post_data = {"title": post.title,
                         "author": post.user.name,
                         "a_uuid": post.user.uuid,
                         "uri": post.uri,
                         "uuid": post.uuid,
                         "content": post.content,
                         "votes": post.total_votes,
                         "voteType": user_vote.value,
                         "tags": post.tag_list,
                         "replies": replies}

            print(post_data)

            # Return post-view template with post_data filled in
            return render_template("post-view.html", data=post_data)

    elif request.method == 'PUT':
        post = Post.query.filter_by(uuid=p_uuid, uri=p_uri).first()

        if not current_user.is_authenticated:
            return {"votes": post.total_votes}, 403

        if post:
            data = request.json
            # Get the incoming VoteType
            v_type = VoteType(data["vote-type"])

            # Query all upvotes for Post
            v_up = PostVote.query.filter((PostVote.user == current_user) &
                                         (PostVote.vote == VoteType.UP) &
                                         (PostVote.post == post)).all()

            # Query all downvotes for Post
            v_down = PostVote.query.filter((PostVote.user == current_user) &
                                           (PostVote.vote == VoteType.DOWN) &
                                           (PostVote.post == post)).all()

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
    abort(404)


@post_bp.route("/posts/<p_uuid>/<p_uri>/reply/", methods=['POST'])
def add_post_reply(p_uuid, p_uri):
    '''
    Defines Flask route to add a reply to a Post

    Methods: POST
    '''

    # If the user is not authenticated, flash them a warning message
    if not current_user.is_authenticated:
        # Create warning message
        url = url_for("auth_bp.login", next=url_for(
            "post_bp.get_post", p_uuid=p_uuid, p_uri=p_uri))
        message = Markup(f'<h1><a href="{url}">Login</a> or'
                         '<a href="/signup">Create Account</a> to post '
                         'reply</h1>')

        # Add message to flash list and reload page
        flash(message, 'error')
        return redirect(url_for("post_bp.get_post",
                                p_uuid=p_uuid,
                                p_uri=p_uri))

    # Get the reply content from the form
    content = bleach.clean(request.form.get('reply-content'))

    if len(content) == 0:
        return "Reply content empty", 409

    post = Post.query.filter_by(uuid=p_uuid).first()

    # Create new Reply object, and add new PostReply to the database
    reply = Reply(content=content)
    print(post.uuid)
    db.session.add(PostReply(user=current_user, post=post, reply=reply))
    db.session.commit()

    # Reload the page to show new reply
    return redirect(url_for("post_bp.get_post",
                            p_uuid=p_uuid,
                            p_uri=p_uri))


@post_bp.route("/posts/<p_uuid>/<p_uri>/", methods=['DELETE'])
@login_required
def handle_post_delete(p_uuid, p_uri):
    '''
    Defines Flask route to delete a Post from database

    Methods: POST
    '''

    post = Post.query.filter_by(uuid=p_uuid, uri=p_uri).first()

    if post:
        db.session.delete(post)
        db.session.commit()
        return "Sucess!", 200
    return "Error", 404


@post_bp.route("/posts/<p_uuid>/<p_uri>/reply/", methods=['PUT'])
def handle_reply_vote(p_uuid, p_uri):
    '''
    Defines Flask route vote on a reply

    Methods: PUT
    '''
    data = request.json
    print(data['uuid'])
    reply = Reply.query.filter_by(uuid=data['uuid']).first()

    if not current_user.is_authenticated:
        return {"votes": reply.total_votes}, 403

    if reply:
        # Get the incoming VoteType
        v_type = VoteType(data["vote-type"])

        # Query all upvotes for Reply
        v_up = ReplyVote.query.filter((ReplyVote.user == current_user) &
                                      (ReplyVote.vote == VoteType.UP) &
                                      (ReplyVote.reply == reply)).all()

        # Query all downvotes for Reply
        v_down = ReplyVote.query.filter((ReplyVote.user == current_user) &
                                        (ReplyVote.vote == VoteType.DOWN) &
                                        (ReplyVote.reply == reply)).all()

        # If user is trying to upvote post
        if v_type == VoteType.UP:
            # Check if the user has downvoted the post, and remove the downvote
            if len(v_down) > 0:
                for v in v_down:
                    db.session.delete(v)
                db.session.commit()

            # If user has not upvoted the post, then add their vote
            if len(v_up) == 0:
                db.session.add(ReplyVote(reply=reply,
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
                db.session.add(ReplyVote(reply=reply,
                                         user=current_user, vote=VoteType.DOWN))
            else:  # If user has already downvoted, then remove their downvote
                for v in v_down:
                    db.session.delete(v)

        # Commit all changes made and return new vote count to front-end
        db.session.commit()
        return {"votes": reply.total_votes}
    return "Not found", 404


@post_bp.route("/posts/<p_uuid>/<p_uri>/reply/", methods=['DELETE'])
@login_required
def handle_reply_delete(p_uuid, p_uri):
    '''
    Defines Flask route to delete a Post from database

    Methods: POST
    '''

    data = request.json
    r_uuid = data['uuid']
    print(r_uuid)
    reply = Reply.query.filter_by(uuid=r_uuid).first()

    if reply:
        db.session.delete(reply)
        db.session.commit()
        return "Sucess!", 200
    return "Error", 404


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

            if (filter["filter"] == "All" or filter["filter"] in tags):
                posts_data.append({"uuid": post.uuid,
                                   "title": post.title,
                                   "uri": post.uri,
                                   "votes": post.total_votes,
                                   "author": post.user.name,
                                   "date": post.date,
                                   "tags": tags})
        return jsonify(posts_data)

    return "Success!", 205


@post_bp.route("/posts/submit/", methods=["GET", 'POST'])
@login_required
def submit_post():
    '''
    Defines Flask route to create a Post

    Methods: POST
    '''
    if request.method == 'POST':
        # Get the reply content from the form
        title = bleach.clean(request.form.get("post-title"), strip=True)
        content = bleach.clean(request.form.get('post-content'), strip=True)
        tag = request.form.get('post-tag')

        if len(title) == 0 or len(content) == 0:
            return "Post content and title cannot be empty", 409

        # Create new Reply object, and add new PostReply to the database
        post = Post(title=title, content=content)
        tag = Tag(TagType(tag))
        post.tags.append(tag)
        current_user.posts.append(post)

        db.session.add_all([post, tag])
        db.session.commit()

        # Reload the page to show new reply
        return redirect(url_for("post_bp.get_post",
                                p_uuid=post.uuid,
                                p_uri=post.uri))
    elif request.method == 'GET':
        return render_template("post-create.html")
