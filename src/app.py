from functools import wraps

from flask import Flask, render_template, session, redirect, url_for, flash, request
from .model.users import users_bp, register_user, login_user, home_page, logout_user, require_role, get_db_connection, get_all_users, update_user_role
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from flask import Flask, render_template
import psycopg2
from .model.report_model import create_flood_report

from .model.emergency_services import (
    create_emergency_dispatch,
    get_dispatches_by_report,
    update_dispatch_status
)

app = Flask(__name__)
app.secret_key = "YourStrongPassword"  # Required for session handling
app.register_blueprint(users_bp)  # Register the Blueprint


def require_login_and_permission(required_perm_level):
    """
    Decorator to check if a user is logged in and meets the required permission level.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('app_login'))
            if session.get('perm_level', 'user') not in required_perm_level:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('app_home'))
            return f(*args, **kwargs)
        return wrapped
    return decorator




@app.route("/")
def hello_world():
    return home_page()

@app.route('/register', methods=['GET', 'POST'])
def app_register():
    """Route for user registration."""
    return register_user()

@app.route('/login', methods=['GET', 'POST'])
def app_login():
    """Route for user login."""
    return login_user()

@app.route('/home')
def app_home():
    """
    Route for the homepage.
    """
    return home_page()
@app.route('/logout')
def app_logout():
    """
    Route for logging out.
    """
    return logout_user()

# @app.route('/manage_roles', methods=['GET', 'POST'])
@require_role('admin')
def manage_roles():
    return update_user_role()

@app.route('/get_all_users')
@require_role('admin')
def get_users():
    return get_all_users()


@app.route('/api/reports', methods=['POST'])
def api_create_report():
    """
    API endpoint to create a new flood report.
    Delegates the functionality to `create_flood_report` in `report_model.py`.
    Returns:
        flask.Response: A JSON response indicating success or failure of the operation.
    """
    return create_flood_report()

@app.route('/report')
def report_form():
    """
    Renders the flood report submission form.
    Returns:
        flask.Response: The rendered HTML form for submitting flood reports.
    """
    return render_template('report_form.html')


@app.route('/api/dispatch', methods=['POST'])
def create_dispatch():
    return create_emergency_dispatch()

@app.route('/api/dispatch/<int:report_id>', methods=['GET'])
def get_dispatch(report_id):
    return get_dispatches_by_report(report_id)

@app.route('/api/dispatch/<int:dispatch_id>', methods=['PUT'])
def update_dispatch(dispatch_id):
    return update_dispatch_status(dispatch_id)

@app.route('/emergencyresponse')
@require_login_and_permission(['admin', 'moderator'])
def emergency_response():
    return render_template("EmergencyResponse.html")