#users.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
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
                print(f"Access denied: User role is {user_role}, required minimum role is {role}")
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('app_home'))
            return f(*args, **kwargs)
        return wrapped
    return decorator


@users_bp.route('/manage_roles', methods=['GET', 'POST'])
@require_role(4) #@require_role('admin')
def manage_roles():
    if request.method == 'POST':
        print("Received POST request")
        print(request.form)
        user_id = request.form['user_id']
        new_role = request.form['perm_level']
        print(f"Updating user {user_id} to role {new_role}")
        try:
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
            return redirect(url_for('Users.manage_roles'))  # Redirect back to manage_roles
        except Exception as e:
            print(f"Error updating user role: {e}")
            flash(f"An error occurred: {e}", 'error')
            return redirect(url_for('Users.manage_roles'))
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT user_id, email, perm_level FROM Users')
        users = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('manage_roles.html', users=users)
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

def get_all_users():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT user_id, email, perm_level FROM Users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users