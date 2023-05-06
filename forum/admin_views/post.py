from flask_admin.contrib.sqla import ModelView
from flask import render_template
from flask_login import current_user
from forum import db
import uuid


class PostView(ModelView):

    '''Defines AdminView for admin control panel'''
    column_hide_backrefs = False
    column_list = ('uuid', 'salt', 'user',
                   'upvotes', 'downvotes')

    # Setup field that are exlcuded from User model table view in admin
    form_excluded_columns = ('uuid', 'salt')
    can_create = False
    can_edit = True

    # Set fields visible when creating new instance of User
    form_create_rules = ('title', 'content', 'tags')

    # Set fields visible when editing instance of User
    form_edit_rules = ('content', 'upvotes', 'downvotes')

    # Set which arguments are visible
    form_widget_args = {
        'uuid': {
            "visible": False
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.static_folder = 'static'

    # Only allow an authenticated admin user through
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return render_template("error/403.html"), 403
