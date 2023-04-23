from http.client import HTTPException
from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import login_required, fresh_login_required, current_user
from . import db
from .models import Course, User, Enrollment
from flask import jsonify
from .role import Role

main = Blueprint('main', __name__)


# Main view
@ main.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    return render_template('index.html')


# 404 errors
@ main.app_errorhandler(404)
def page_not_found(e):
    print(e)
    return render_template('error/404.html'), 404


# 403 errors
@ main.app_errorhandler(403)
def forbidden(e):
    print(e)
    return render_template('error/403.html'), 403


@ main.route('/courses', methods=['GET'])
@login_required
def courses():
    # Take admin user to the admin page, admin has no courses
    if current_user.is_admin():
        return redirect("/admin")

    # Take user to the teacher or student view based on role
    if current_user.role == Role.PROFESSOR:
        return render_template('teacher.html')
    elif current_user.role == Role.STUDENT:
        return render_template('courses.html')
    # Anyone else gets index
    return render_template('index.html')


@ main.route('/courses/<c_id>', methods=['GET'])
@login_required
def course(c_id):
    # Get course and professor tied to that course
    course = Course.query.filter_by(course_id=c_id).first()
    prof = User.query.join(Enrollment).join(Course).filter(
        (User.role == Role.PROFESSOR) & (Course.course_id == c_id)).all()

    # If ID mismatch we are not allowed to be here
    access = False
    for p in prof:
        print(p)
        if p.user_id == current_user.user_id:
            access = True

    if not access or len(prof) == 0:
        return redirect(url_for("main.courses"))

    # If prof then can view student roster
    if course:
        return render_template('courseGrades.html', c_id=c_id, course=course.name)
    abort(404)


@ main.route('/courses/<c_id>/students', methods=['GET'])
@login_required
def get_course_students(c_id):
    # Get all students in course by id
    enrollments = Enrollment.query.join(User).join(Course).filter(
        (User.role == Role.STUDENT) & (Course.course_id == c_id)).all()

    if len(enrollments) == 0:
        return redirect(url_for("main.courses"))

    output = []
    for e in enrollments:
        if e.user is None:
            continue
        # Send id, name, and grade data per student
        user = {"id": e.user_id, "name": e.user.name, "grade": e.grade}
        output.append(user)
    return jsonify(output)


@ main.route('/getCourses', methods=['GET'])
@ login_required
def get_courses():
    classes = Course.query.all()

    output = []

    for c in classes:
        in_class = False

        # Check if user is in this course
        for e in current_user.enrollment:
            if c == e.course:
                in_class = True

        # Create dict for each course listing availability and enrollment status
        course_data = {'courseId': c.course_id, 'courseName': c.name, 'prof': c.prof_name,
                       'time': c.time, 'enrolled': c.enrolled, 'maxEnroll': c.max_enroll, "in_class": in_class}
        output.append(course_data)

    return jsonify(output)


@ main.route('/getEnrolled', methods=['GET'])
@ login_required
def get_enrolled():
    output = []

    if len(current_user.enrollment) == 0:
        return {}, 200

    # Get all enrolled courses for user
    for e in current_user.enrollment:
        c = e.course

        # Create dict for each course
        course_data = {'courseId': c.course_id, 'courseName': c.name, 'prof': c.prof_name,
                       'time': c.time, 'enrolled': c.enrolled, 'maxEnroll': c.max_enroll}
        output.append(course_data)
    return jsonify(output)


@ main.route('/courses/add', methods=['POST'])
@ login_required
def add_course():
    # Get the id of the course the user wants to add and query db
    data = request.json
    c_id = data['courseId']
    course = Course.query.filter_by(course_id=c_id).first()

    # Try to enroll in the course
    try:
        if course:
            course.add_user(current_user)
            db.session.commit()
            return "Enrolled student in course", 205
    except Exception as e:
        return "Course full", 409


@ main.route('/courses/remove/<c_id>', methods=['DELETE'])
@ login_required
def remove_course(c_id):
    enrollment = Enrollment.query.join(Course).join(User).filter(
        ((Course.course_id == c_id) & (User.user_id == current_user.user_id)))
    enrollment = enrollment.first()

    # If the enrollment exists, delete it
    if enrollment:
        enrollment.course.remove_user(current_user)
        db.session.commit()
        print(f"De-Enrolled student from {c_id}")
        return "Success!", 205
    return "Student not enrolled in course", 404


@ main.route('/courses/<c_id>/students', methods=['PUT'])
@ login_required
def update_grades(c_id):
    data = request.json

    for user in data:
        for key, value in user.items():
            # Get each student based on incoming ids
            user = Enrollment.query.join(Course).join(User).filter(
                (User.role == Role.STUDENT) & (User.user_id == key) & (Course.course_id == c_id)).first()

            if not user:
                abort(404)
            # Update the value of the user grade
            user.grade = value
    db.session.commit()
    return "Success!", 205
