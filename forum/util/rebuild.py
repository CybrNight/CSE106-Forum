import os
from random import randint, choice, shuffle
from time import sleep


def create_posts():
    from forum import db
    from forum.models import User, Post, Tag, Reply, PostReply, TagType
    '''Creates a set number of random posts when rebuilding the database'''
    path = os.getcwd()
    path = os.path.join(path, "forum/util/post.txt")

    post_text = ""
    with open(path, 'r') as file:
        post_text = file.read()

    posts = {}
    replies = []
    reply_content = ["#PETA FOREVER YOU PEOPLE ARE MURDERERS",
                     "I love meat", "BEEF, It's what's for dinner b*tch"]
    users = User.query.all()

    for i in range(0, 25):
        type = choice(list(TagType))
        posts.update({Post(title=f"Post{i+1}"): Tag(type=type)})

        for j in range(0, 5):
            replies.append(Reply(content=choice(reply_content)))

    for user in users:
        if not len(posts) > 0:
            continue

        post, tag = choice(list(posts.items()))
        del posts[post]
        post.content = post_text
        post.tags.append(tag)
        user.posts.append(post)
        db.session.add_all([post, tag])
        if len(replies) > 0:
            a = randint(2, 4)
            for j in range(1, a):
                shuffle(replies)
                reply = replies.pop()
                reply.content = choice(reply_content)
                db.session.add_all([user, post, reply])
                db.session.add(PostReply(user=user, post=post, reply=reply))

    db.session.commit()
    print("Committed Course data to database")


def create_users():
    from forum import db
    from forum.models import Role, User
    '''Creates default users for testing'''
    # Create user acccounts
    ralph = User(name="Ralph Jenkins", role=Role.DEFAULT)
    susan = User(name="Suan Walker", role=Role.DEFAULT)
    ammon = User(name="Ammon Hepworth", role=Role.DEFAULT)
    jose = User(name="Jose Santos")
    betty = User(name="Betty Brown")
    john = User(name="John Stuart")
    li = User(name="Li Cheng")
    mindy = User(name="Mindy Cheng")
    aditya = User(name="Aditya Ranganath")
    yi = User(name="Yi Wen Chen")
    nancy = User(name="Nancy Little")

    db.session.add_all([ralph, susan, ammon, jose, betty,
                        john,
                        mindy,
                        aditya,
                        yi, li, nancy])

    db.session.commit()
    print("Committed User accounts to database")


def rebuild_db(test_data=False):
    from forum import db, create_app
    '''Rebuilds the database with test data'''
    from forum.models import User, Role

    # Create new app object
    app = create_app()
    app.app_context().push()
    print("Created app context")
    sleep(0.1)

    # Re-build all tables
    db.drop_all()

    print("Dropped all table in database")
    sleep(0.1)

    db.create_all()

    print("Created database tables")
    sleep(0.1)

    if test_data:
        # Generate placeholder users and post content
        print("Generating test data:")
        sleep(0.1)

        create_users()
        print("Generated user accounts")
        sleep(0.1)

        create_posts()
        print("Generated placehold post content")
        sleep(0.1)

    # Add default admin account
    db.session.add(User(role=Role.ADMIN, name="ADMIN",
                        email="admin@me.com"))
    print("Created ADMIN user account")

    db.session.commit()
    print("Committed all changes to database")
