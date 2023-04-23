from flask_admin import Admin, expose
from flask_admin.contrib.sqla import ModelView
from flask import session, render_template, flash, request
from flask_login import current_user
from .models import Role, User, Enrollment, Course
from sqlalchemy.exc import IntegrityError
from project.main import db
import uuid


class AdminView(ModelView):
    # Setup columns to show in main view
    column_hide_backrefs = False
    column_list = ('user_id', 'email', 'name', 'role',
                   'enrollment')

    inline_models = (Enrollment,)

    # Setup fields that can be modified during creation/editing
    form_excluded_columns = ('user_id', 'enrollment')

    form_create_rules = ('email', 'name', 'password', 'role')

    form_edit_rules = ('email', 'name', 'password', 'role',
                       'enrollment')

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

        # Check if any courses are over enrollment
        for e in model.enrollment:
            # Update course enroll values
            e.course.set_enroll_count()

            # Rollback changes made to db and throw exception if course over enrollment
            if e.course.enrolled > e.course.max_enroll:
                db.session.rollback()
                raise ValueError(f"Class ({e.course}) above capacity")
        db.session.commit()
        return True

    # Updates the model after changes are done
    def after_model_change(self, form, model, is_created):
        for e in model.enrollment:
            if e is None:
                continue

            if e.course:
                e.course.set_enroll_count()
        db.session.commit()


class CourseView(ModelView):
    # Setup columns to show in view
    column_hide_backrefs = False
    column_list = ('course_id', 'name', 'prof_name', 'time', 'enrolled',
                   'max_enroll', 'enrollment')

    inline_models = (Enrollment,)

    # Setup columns for edit/create mode
    form_excluded_columns = ('course_id', 'enrollment')

    form_create_rules = ('name', 'time',
                         'max_enroll')
    form_edit_rules = ('name', 'prof_name', 'time', 'enrolled',
                       'max_enroll', 'enrollment')

    form_widget_args = {
        'enrolled': {
            'disabled': True
        },
        'prof_name': {
            'disabled': True
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.static_folder = 'static'

    # Called when model is updated
    def on_model_change(self, form, model, is_created):
        if is_created:
            course_id = uuid.uuid4().hex[:8]
            exists = db.session.query(Course.course_id).filter_by(
                course_id=course_id).first() is not None

            while exists:
                course_id = uuid.uuid4().hex[:8]

            model.course_id = course_id
        model.set_enroll_count()

        # Check if course is over capacity
        if model.enrolled > model.max_enroll:

            # Rollback changes and show error to user
            db.session.rollback()
            raise ValueError(f"Class ({model.name}) above capacity")

        db.session.commit()
        return True

    def after_model_change(self, form, model, is_created):
        model.update()
        db.session.commit()
