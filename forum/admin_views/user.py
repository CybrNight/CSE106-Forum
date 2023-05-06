from flask_admin.contrib.sqla import ModelView
from flask import render_template
from flask_login import current_user
from forum import db
import uuid

from werkzeug.security import gen_salt
from forum.util import gen_model_uuid


class UserView(ModelView):

    '''Defines AdminView for admin control panel'''
    column_hide_backrefs = False
    column_list = ('uuid', 'salt', 'email', 'name', 'role')

    # Setup field that are exlcuded from User model table view in admin
    form_excluded_columns = ('uuid')

    # Set fields visible when creating new instance of User
    form_create_rules = ('email', 'name', 'password', 'role')

    # Set fields visible when editing instance of User
    form_edit_rules = ('email', 'name', 'password', 'role')

    can_create = False
    can_edit = True

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
