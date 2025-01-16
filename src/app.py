from functools import wraps

from flask import Flask, render_template, session, redirect, url_for, flash, request, jsonify
from .model.users import users_bp, register_user, login_user, home_page, logout_user, require_role, get_db_connection, get_all_users, update_user_role
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
import psycopg2
from .model.report_model import (
    create_flood_report,
    get_all_reports,
    get_unverified_reports,
    reject_report,
    verify_report
    )

from .model.emergency_services import (
    create_emergency_dispatch,
    get_dispatches_by_report,
    update_dispatch_status,
    get_all_dispatches,
    delete_dispatch
)

app = Flask(__name__)
app.secret_key = "YourStrongPassword"  # Required for session handling
app.register_blueprint(users_bp)  # Register the Blueprint
app.config['DEBUG'] = True #For development, we can configure Flask to show error tracebacks



def require_login_and_permission(required_perm_level):
    """
    Decorator to check if a user is logged in and meets the required permission level.

    This function ensures that some URLs can be protected
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            perm_level = session.get('perm_level', 0)  # Default to 0 (logged out)
            if perm_level < required_perm_level:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('login_user'))  # Redirect to login page
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.route("/historical_data")
def historical_data():
    from .model.users import historical_page
    return historical_page()

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

@app.route('/api/user_email')
def get_user_email():
    user_email = session.get('email', '')  # Get email from session
    return jsonify({"email": user_email})


@app.route('/api/dispatch', methods=['POST'])
def create_dispatch():
    return create_emergency_dispatch()

@app.route('/api/dispatch/<int:report_id>', methods=['GET'])
def get_dispatch(report_id):
    return get_dispatches_by_report(report_id)

@app.route('/api/dispatch/<int:dispatch_id>', methods=['PUT'])
def update_dispatch(dispatch_id):
    return update_dispatch_status(dispatch_id)

@app.route('/api/dispatches', methods=['GET'])
@require_login_and_permission(3)  # Protect route for users with permission level 3 or above
def fetch_dispatches():
    """
    API route to retrieve all active emergency dispatches.

    Returns:
        flask.Response: The JSON response from the `get_all_dispatches` function.
    """
    return get_all_dispatches()

@app.route("/api/dispatch/<int:dispatch_id>", methods=["DELETE"])
def remove_dispatch(dispatch_id):
    return delete_dispatch(dispatch_id)


@app.route('/emergencyresponse')
@require_login_and_permission(3)
def emergency_response():
    return render_template("EmergencyResponse.html")

@app.route("/api/reports", methods=["GET"])
def api_get_all_reports():
    return get_all_reports()


@app.route('/manage_reports')
@require_login_and_permission(2)
def manage_reports():
    """
    Renders the manage reports page.

    Returns:
        flask.Response: The rendered HTML template for managing reports.
    """
    return render_template("manage_reports.html")

@app.route('/all_reports')
@require_login_and_permission(2)
def display_reports():
    return render_template("all_reports.html")

@app.route('/api/unverified_reports', methods=['GET'])
@require_login_and_permission(2)
def fetch_unvertified_reports():
    """
    API route to retrieve all unverified reports.
    """
    return get_unverified_reports()

@app.route('/api/unverified_reports/<int:report_id>/verify', methods=['PUT'])
@require_login_and_permission(2) 
def verify_report_api(report_id):
    """
    API route to verify a report.
    """
    return verify_report(report_id)

@app.route('/api/unverified_reports/<int:report_id>/reject', methods=['PUT'])
@require_login_and_permission(2)
def reject_report_api(report_id):
    """
    API route to reject a report.
    """
    return reject_report(report_id)


@app.route('/profile', methods=['GET'])
@app.route('/profile/<int:user_id>', methods=['GET'])
def profile_page(user_id=None):
    from .model.users import profile_page
    return profile_page(user_id)

@app.route('/profile/edit', methods=['GET', 'POST'])
@app.route('/profile/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_profile(user_id=None):
    from .model.users import edit_profile
    return edit_profile(user_id)

@app.route('/request_promotion', methods=['POST'])
def request_promotion():
    from .model.users import request_promotion
    return request_promotion()

@app.route('/api/get_flood_reports', methods=['GET'])
def getUserReports():
    from .model.users import get_flood_reports
    return get_flood_reports()