from flask_admin.contrib.sqla import ModelView
from flask import render_template
from flask_login import current_user
from forum import db
import uuid


class UserView(ModelView):

    '''Defines AdminView for admin control panel'''
    column_hide_backrefs = False
    column_list = ('uuid', 'email', 'name', 'role')

    # Setup field that are exlcuded from User model table view in admin
    form_excluded_columns = ('uuid', 'salt')

    # Set fields visible when creating new instance of User
    form_create_rules = ('email', 'name', 'password', 'role')

    # Set fields visible when editing instance of User
    form_edit_rules = ('email', 'name', 'password', 'role')

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

    def on_model_change(self, form, model, is_created):
        from forum.models import User

        # Generate new uuid for user_id
        if is_created:
            user_id = uuid.uuid4().hex[:8]

            # Get all existing uuid from db
            exists = db.session.query(User.user_id).filter_by(
                user_id=user_id).first() is not None

            # Continue generating while non-unique
            while exists:
                user_id = uuid.uuid4().hex[:8]

            model.user_id = user_id
        return True
