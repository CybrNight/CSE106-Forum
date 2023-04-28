from flask_admin import Admin, expose
from flask_admin.contrib.sqla import ModelView
from flask import session, render_template, flash, request
from flask_login import current_user
from .models import Role, User
from sqlalchemy.exc import IntegrityError
from project.main import db
import uuid


class AdminView(ModelView):
    # Setup columns to show in main view
    column_hide_backrefs = False
    column_list = ('user_id', 'email', 'name', 'role')

    # Setup fields that can be modified during creation/editing
    form_excluded_columns = ('user_id')

    form_create_rules = ('email', 'name', 'password', 'role')

    form_edit_rules = ('email', 'name', 'password', 'role')

    form_widget_args = {
        'user_id': {
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
