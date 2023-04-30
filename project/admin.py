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
    column_list = ('uuid', 'email', 'name', 'role')

    # Setup fields that can be modified during creation/editing
    form_excluded_columns = ('uuid')

    form_create_rules = ('email', 'name', 'password', 'role')

    form_edit_rules = ('email', 'name', 'password', 'role')

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
        # Generate new uuid for user
        if is_created:
            temp_uuid = uuid.uuid4().hex[:8]

            # Get all existing uuid from db
            exists = db.session.query(User.uuid).filter_by(
                uuid=temp_uuid).first() is not None

            # Continue generating while non-unique
            while exists:
                temp_uuid = uuid.uuid4().hex[:8]

            model.uuid = temp_uuid
        return True
