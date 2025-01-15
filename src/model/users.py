#users.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import psycopg2.extras 
from psycopg2.extras import DictCursor  #for the get_all_users function

users_bp = Blueprint('Users', __name__)

def get_db_connection():
    print("Connecting to the database...")
    conn = psycopg2.connect(
        dbname="AFM",
        user="afm_user",
        password="afm_password",
        host="db",
        port=5432
    )
    print("Connected to the database.")
    return conn



# Checks for MINIMUM role level
def require_role(role):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user_role = int(session.get('perm_level', 0))
            if user_role < role:
                print(f"[DEBUG] Access denied: User role is {user_role}, required minimum role is {role}")
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('app_home'))
            print(f"[DEBUG] Access granted: User role is {user_role}") #for Better Debugging
            return f(*args, **kwargs)
        return wrapped
    return decorator




@users_bp.route('/manage_roles', methods=['GET', 'POST'])
@require_role(4)
def manage_roles():
    if request.method == 'POST':
        # Handle role updates
        try:
            user_id = request.form['user_id']
            new_role = request.form['perm_level']
            print(f"Updating user {user_id} to role {new_role}")
            
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                'UPDATE Users SET perm_level = %s WHERE user_id = %s',
                (new_role, user_id)
            )
            conn.commit()
            cur.close()
            conn.close()
            flash('User role updated successfully!', 'success')
        except Exception as e:
            print(f"Error updating user role: {e}")
            flash(f"An error occurred: {e}", 'error')
        
        return redirect(url_for('Users.manage_roles'))

    # Handle GET requests for searching or listing all users
    filter_type = request.args.get('filter_type')
    filter_value = request.args.get('filter_value')
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=DictCursor)
        
        if filter_type and filter_value:
            query = 'SELECT user_id, email, perm_level FROM Users'
            params = ()
            
            if filter_type == 'email':
                query += ' WHERE email ILIKE %s'
                params = (f"%{filter_value}%",)
            elif filter_type == 'user_id':
                query += ' WHERE user_id = %s'
                try:
                    params = (int(filter_value),)
                except ValueError:
                    flash("User ID must be a number", "error")
                    return redirect(url_for('Users.manage_roles'))
            elif filter_type == 'role':
                query += ' WHERE perm_level = %s'
                try:
                    params = (int(filter_value),)
                except ValueError:
                    flash("Role must be a number", "error")
                    return redirect(url_for('Users.manage_roles'))

            print(f"Executing query: {query} with params {params}")
            cur.execute(query, params)
            users = cur.fetchall()
        else:
            users = get_all_users()
        
        cur.close()
        conn.close()
        
        return render_template('manage_roles.html',
            users=users,
            perm_level=session.get('perm_level', 0),
            user_email=session.get('user_email')
        )
    except Exception as e:
        print(f"Error fetching users: {e}")
        flash(f"An error occurred: {e}", 'error')
        return redirect(url_for('app_home'))


def register_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        phone_num = request.form.get('phone_num')  # Optional field
        user_address = request.form.get('user_address')  # Optional field

        # Check for password mismatch
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('app_register'))

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
#        hashed_password = generate_password_hash(password)

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            # Insert user into the Users table
            cur.execute(
                'INSERT INTO Users (email, hashed_passw, phone_num, user_address) VALUES (%s, %s, %s, %s)',
                (email, hashed_password, phone_num, user_address)
            )
            conn.commit()
            cur.close()
            conn.close()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('app_login'))
        except Exception as e:
            flash(f'Registration failed: {e}', 'error')
            return redirect(url_for('app_register'))

    return render_template('register.html')

def home_page():
    """
    Render the homepage and set appropriate context based on login status.
    """
    perm_level = session.get('perm_level', 0)  # Default to 0 (not logged in)
    user_email = session.get('email', None)  # Get user's email if logged in
    return render_template('index.html', perm_level=int(perm_level), user_email=user_email)

def historical_page():
    perm_level = session.get('perm_level', 0)  # Default to 0 (not logged in)
    user_email = session.get('email', None)  # Get user's email if logged in
    return render_template('historical_data.html', perm_level=int(perm_level), user_email=user_email)

@users_bp.route('/login', methods=['GET', 'POST'])
def login_user():
    # Check if the user is already logged in
    if 'user_id' in session:
        return redirect(url_for('app_home'))  # Redirect to the home page if already logged in

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)  # Use DictCursor here

        # Query the Users table by email
        cur.execute('SELECT * FROM Users WHERE email = %s', (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        # Authenticate user
        if user and check_password_hash(user['hashed_passw'], password):
            # Set session variables without converting perm_level
            session['user_id'] = user['user_id']
            session['email'] = user['email']
            session['perm_level'] = user['perm_level']

            flash('Login successful!', 'success')
            return redirect(url_for('app_home'))  # Redirect to the home page

        # If authentication fails
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')

@users_bp.route('/logout')
def logout_user():
    """
    Clear the session and redirect to the login page.
    """
    session.clear()  # Clear the session data
    flash('You have been logged out.', 'success')
    return redirect(url_for('app_home'))  # Redirect to home page

def update_user_role(user_id, perm_level):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Users SET perm_level = %s WHERE user_id = %s", (perm_level, user_id))
    conn.commit()
    cur.close()
    conn.close()

def get_all_users(): # to list all users
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT user_id, email, perm_level FROM Users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users

@users_bp.route('/profile/<int:user_id>', methods=['GET'])
@users_bp.route('/profile', methods=['GET'])
def profile_page(user_id=None):
    """
    Display user profile information.
    """
    is_admin_view = user_id is not None and int(session.get('perm_level', 0)) >= 4
    logged_in_user_id = session.get('user_id')
    
    if not user_id:
        user_id = logged_in_user_id
    if not user_id:
        flash("Unauthorized access to the profile page.", "error")
        return redirect(url_for('app_home'))

    user = fetch_user_profile(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for('app_home'))

    return render_template(
        'profile.html',
        user=user,
        is_admin_view=is_admin_view,
        perm_level=session.get('perm_level', 0),
        user_email=session.get('email', '')
    )



@users_bp.route('/api/get_flood_reports', methods=['GET'])
def get_flood_reports():
    """Fetch flood reports for a specific user."""
    email = request.args.get('email')

    if not email:
        return jsonify({"error": "Email is required."}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=DictCursor)

        # Fetch flood reports for the user
        cur.execute(
            """SELECT ID, Severity, Verified FROM FloodReport WHERE associatedemail = %s""",
            (email,)
        )
        reports = cur.fetchall()

        cur.close()
        conn.close()

        # Transform results into JSON serializable format
        result = [
            {
                "ID": report["id"],
                "Severity": report["severity"],
                "Verified": report["verified"]
            }
            for report in reports
        ]
        print (result)
        return jsonify(result), 200

    except Exception as e:
        print(f"Error fetching flood reports: {e}")
        return jsonify({"error": "An error occurred while fetching flood reports."}), 500



def fetch_user_profile(user_id):
    """
    Fetches user details by user_id.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(
            "SELECT user_id, email, phone_num, user_address, perm_level FROM Users WHERE user_id = %s",
            (user_id,)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user:
            raise ValueError("User not found.")

        return user
    except Exception as e:
        print(f"Error fetching user profile: {e}")
        return None



def update_user_profile(user_id, email, phone_num, user_address):
    """
    Updates user email and phone number.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE Users SET email = %s, phone_num = %s, user_address = %s WHERE user_id = %s", (email, phone_num,user_address, user_id))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error updating user profile: {e}")
        raise e



def change_user_password(user_id, current_password, new_password):
    """
    Changes the user password after validating the current password.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Fetch current hashed password
        cur.execute("SELECT hashed_passw FROM Users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
        if not user:
            raise ValueError("User not found.")
        # Validate current password
        if not check_password_hash(user['hashed_passw'], current_password):
            raise ValueError("Invalid current password.")
        # Update to the new hashed password
        hashed_password = generate_password_hash(new_password)
        cur.execute("UPDATE Users SET hashed_passw = %s WHERE user_id = %s", (hashed_password, user_id))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error changing user password: {e}")
        raise e


@users_bp.route('/profile/edit/<int:user_id>', methods=['GET', 'POST'])
@users_bp.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile(user_id=None):
    """
    Edit profile page with all the form functionality.
    """
    is_admin_view = user_id is not None and int(session.get('perm_level', 0)) >= 4
    logged_in_user_id = session.get('user_id')
    
    if not user_id:
        user_id = logged_in_user_id
    if not user_id:
        flash("Unauthorized access to edit profile.", "error")
        return redirect(url_for('app_home'))

    if request.method == 'POST':
        try:
            if 'email' in request.form:
                email = request.form['email']
                phone_num = request.form['phone_num']
                user_address = request.form['user_address']
                update_user_profile(user_id, email, phone_num, user_address)
                flash("Profile updated successfully.", "success")
                return redirect(url_for('Users.edit_profile', user_id=user_id))
            elif 'current_password' in request.form and 'new_password' in request.form:
                current_password = request.form['current_password']
                new_password = request.form['new_password']
                change_user_password(user_id, current_password, new_password)
                flash("Password updated successfully.", "success")
                return redirect(url_for('Users.edit_profile', user_id=user_id))

        except ValueError as ve:
            flash(str(ve), "error")
        except Exception as e:
            print(f"Unexpected error: {e}")
            flash(f"An unexpected error occurred: {e}", "error")

    user = fetch_user_profile(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for('app_home'))

    return render_template(
        'edit_profile.html',
        user=user,
        is_admin_view=is_admin_view,
        perm_level=session.get('perm_level', 0),
        user_email=session.get('email', '')
    )



from datetime import datetime, timedelta
from flask_mail import Mail, Message

def send_promotion_email(email, new_role):
    """Send email notification for promotion."""
    try:
        mail = Mail()
        msg = Message(
            'Your Promotion Request Has Been Approved',
            sender='noreply@yourapp.com',
            recipients=[email]
        )
        msg.body = f'Congratulations! You have been promoted to {new_role}.'
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")

@users_bp.route('/request_promotion', methods=['POST'])
def request_promotion():
    """Handle user requests for role promotion."""
    try:
        user_id = session.get('user_id')
        requested_role = request.form.get('requested_role')

        if not requested_role:
            flash("Please select a role to request.", "error")
            return redirect(url_for('Users.profile_page'))

        requested_role = int(requested_role)
        if requested_role not in [2, 3]:
            flash("Invalid role request.", "error")
            return redirect(url_for('Users.profile_page'))

        conn = get_db_connection()
        cur = conn.cursor()

        # Get user email and rejection status
        cur.execute(
            "SELECT email, last_rejected_on, ESRejected FROM Users WHERE user_id = %s",
            (user_id,)
        )
        user_data = cur.fetchone()
        if not user_data:
            flash("User not found.", "error")
            return redirect(url_for('Users.profile_page'))

        email, last_rejected, es_rejected = user_data

        # Check for Emergency Service specific conditions
        if requested_role == 3:  # Emergency Service
            if not '@gov' in email.lower():
                flash("Emergency Service requests are only available for government email addresses.", "error")
                return redirect(url_for('Users.edit_profile'))
            
            if es_rejected:
                flash("You have been permanently banned from requesting Emergency Service role.", "error")
                return redirect(url_for('Users.edit_profile'))
        
        # Check for Moderator temporary ban
        elif requested_role == 2 and last_rejected:  # Moderator
            if (datetime.now() - last_rejected).days < 28:
                flash("You must wait 4 weeks after a rejection to request Moderator role again.", "error")
                return redirect(url_for('Users.edit_profile'))

        # Check for existing pending request
        cur.execute(
            "SELECT * FROM PromotionRequests WHERE user_id = %s AND status = 'pending'",
            (user_id,)
        )
        if cur.fetchone():
            flash("You already have a pending promotion request.", "error")
        else:
            role_type = 'Moderator' if requested_role == 2 else 'Emergency Service'
            cur.execute(
                """INSERT INTO PromotionRequests 
                   (user_id, requested_role, status, type) 
                   VALUES (%s, %s, 'pending', %s)""",
                (user_id, requested_role, role_type)
            )
            conn.commit()
            flash("Promotion request submitted successfully.", "success")

        cur.close()
        conn.close()
    except Exception as e:
        flash(f"An error occurred: {e}", "error")
    flash('Your promotion request has been sent successfully.')
    return redirect(url_for('Users.edit_profile'))


@users_bp.route('/promotion_requests', defaults={'role': None})
@users_bp.route('/promotion_requests/<int:role>')
@require_role(4)  # Requires admin access
def view_promotion_requests(role):
    """Display promotion requests filtered by role."""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Define valid roles and their display names
        valid_roles = {2: 'Moderator', 3: 'Emergency Service'}
        
        # If a specific role is provided, validate it
        if role is not None and role not in valid_roles:
            flash("Invalid role filter.", "error")
            return redirect(url_for('app_home'))
        
        # Fetch promotion requests based on the role filter
        if role is None:
            # No role specified: fetch all pending requests
            cur.execute(
                """SELECT pr.request_id, u.email, pr.created_at, pr.requested_role 
                   FROM PromotionRequests pr 
                   JOIN Users u ON pr.user_id = u.user_id 
                   WHERE pr.status = 'pending'"""
            )
        else:
            # Fetch requests for the specified role
            cur.execute(
                """SELECT pr.request_id, u.email, pr.created_at, pr.requested_role 
                   FROM PromotionRequests pr 
                   JOIN Users u ON pr.user_id = u.user_id 
                   WHERE pr.requested_role = %s AND pr.status = 'pending'""",
                (role,)
            )
        
        requests = cur.fetchall()
        cur.close()
        conn.close()

        return render_template(
            'promotion_requests.html',
            requests=requests,
            role_name=valid_roles.get(role, 'All Requests'),
            current_role=role,
            perm_level=session.get('perm_level', 0),  # Match the other routes
            user_email=session.get('user_email')      # Match the other routes
        )
    except Exception as e:
        print(f"Error viewing promotion requests: {e}")  # Logging
        flash(f"An error occurred: {e}", "error")
        return redirect(url_for('app_home'))



@users_bp.route('/handle_promotion_request/<int:request_id>', methods=['POST'])
@require_role(4)
def handle_promotion_request(request_id):
    """Handle accepting or rejecting promotion requests."""
    action = request.form.get('action')
    if action not in ['accept', 'reject']:
        flash("Invalid action.", "error")
        return redirect(url_for('Users.view_promotion_requests', role=2))

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get request details first
        cur.execute(
            """SELECT pr.user_id, pr.requested_role, u.email 
               FROM PromotionRequests pr
               JOIN Users u ON pr.user_id = u.user_id
               WHERE pr.request_id = %s AND pr.status = 'pending'""",
            (request_id,)
        )
        request_data = cur.fetchone()
        
        if not request_data:
            flash("Request not found or already processed.", "error")
            return redirect(url_for('Users.view_promotion_requests', role=2))

        user_id, requested_role, user_email = request_data

        if action == 'accept':
            # Update user's role
            cur.execute(
                "UPDATE Users SET perm_level = %s WHERE user_id = %s",
                (requested_role, user_id)
            )
            status = 'accepted'
            flash("Promotion request accepted.", "success")
            # Send email notification
            role_name = 'Moderator' if requested_role == 2 else 'Emergency Service'
            send_promotion_email(user_email, role_name)
        else:
            status = 'rejected'
            if requested_role == 3:  # Emergency Service rejection
                # Set permanent ban
                cur.execute(
                    "UPDATE Users SET ESRejected = TRUE WHERE user_id = %s",
                    (user_id,)
                )
                flash("Emergency Service request rejected. User has been permanently banned from requesting this role.", "success")
            else:  # Moderator rejection
                # Update last_rejected_on for temporary ban
                cur.execute(
                    "UPDATE Users SET last_rejected_on = CURRENT_TIMESTAMP WHERE user_id = %s",
                    (user_id,)
                )
                flash("Moderator request rejected. User must wait 4 weeks before requesting again.", "success")

        # Update request status
        cur.execute(
            """UPDATE PromotionRequests 
               SET status = %s, 
                   rejected_on = CASE WHEN %s = 'rejected' THEN CURRENT_TIMESTAMP ELSE NULL END 
               WHERE request_id = %s""",
            (status, status, request_id)
        )
        
        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error handling promotion request: {e}")
        flash(f"An error occurred: {e}", "error")
        return redirect(url_for('Users.view_promotion_requests', role=2))

    # Always redirect to the same role view that was being processed
    return redirect(url_for('Users.view_promotion_requests', role=requested_role))