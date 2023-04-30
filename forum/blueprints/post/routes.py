from flask import Blueprint, redirect, render_template, request, url_for
from flask import flash
from flask_login import current_user
from markupsafe import Markup
from flask import jsonify

from forum.models import Reply, PostReply, Post
from forum import db

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


@post_bp.route("/posts/<p_uuid>/<p_title>/", methods=['GET'])
def get_post(p_uuid, p_title):
    '''
    Defines Flask route to retrieve specific post

    Methods: GET
    '''

    if request.method == 'GET':
        if p_title == "testpost":
            # If testpost is being loaded, then load the first Post in db
            post = Post.query.all()[0]
        else:
            # Query post with UUID
            post = Post.query.join(PostReply).filter(
                Post.uuid == p_uuid).first()

        # If we found the post then retrieve its data
        if post:
            replies = []
            # Get each PostReply entry from the post
            for p_reply in post.post_replies:
                # Get the user, and reply information from the PostReply
                user, _, reply = p_reply.get()

                # Store each Reply object data as JSON
                replies.append(
                    {"author": user.name,
                     "content": reply.content,
                     "upvotes": reply.total_votes})

            # For the queried post, store its metadata and replies data in JSON
            post_data = {"uuid": post.uuid,
                         "title": post.title,
                         "content": post.content,
                         "upvotes": post.total_votes,
                         "tags": post.tag_list,
                         "replies": replies}
            print(post_data)

            # Return post-view template with post_data filled in
            return render_template("post-view.html", data=post_data)

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
        message = Markup('< h1 > <a href="/login" > Login < /a > or'
                         '< a href="/signup" > Create Account < /a > to post'
                         'reply < /h1 >')

        # Add message to flash list and reload page
        flash(message, 'error')
        return redirect(url_for("post_bp.get_post",
                                p_uuid=p_uuid,
                                p_title=p_title))

    # Get the reply content from the form
    content = request.form.get('reply-content')
    post = Post.query.join(PostReply).filter(Post.title == p_title).first()

    # Create new Reply object, and add new PostReply to the database
    reply = Reply(content=content)
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


@post_bp.route('/getPosts/', methods=['GET'])
def get_posts():
    '''
    Define Flask route to return list of all posts as JSON data to client

    Methods: GET
    '''

    if request.method == 'GET':
        posts = Post.query.all()
        posts_data = []
        for post in posts:
            tags = []
            for tag in post.tags:
                tags.append(tag.type.value)

            posts_data.append({"uuid": post.uuid,
                               "title": post.title,
                               "upvotes": post.total_votes,
                               "author": post.user.name,
                               "date": post.date,
                               "tags": tags})
        return jsonify(posts_data)

    return "Success!", 205


@ post_bp.route("/posts/add/", methods=['POST'])
def add_post():
    data = request.json
    print(data)
    return "Success!", 205
