import psycopg2
import random
from flask import request, jsonify

# Database connection function
def get_db_connection():
    """
    Establishes and returns a connection to the PostgreSQL database.

    Returns:
        psycopg2.extensions.connection: A connection object to the PostgreSQL database.
    """
    conn = psycopg2.connect(
        dbname="AFM",
        user="afm_user",
        password="afm_password",
        host="db",
        port=5432
    )
    return conn

# Function to create a flood report
def create_flood_report():
    """
    Handles the creation of a flood report in the database.
    """
    data = request.json
    try:
        # Extract and validate required fields
        email = data.get('email').strip().lower()
        severity = data.get('severity')
        lat = data.get('lat')
        lng = data.get('long')

        if not email or not severity:
            return jsonify({"error": "Email and severity are mandatory"}), 400

        location = f"{lat},{lng}"  # Combine lat/lng into location string

        # Optional fields
        phone_number = data.get('phone_number') or None
        description = data.get('description') or None

        print("Processing flood report:")
        print("Email:", email)
        print("Severity:", severity)
        print("Location:", location)
        print("Phone Number:", phone_number)
        print("Description:", description)

        # Insert into the database
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            '''
            INSERT INTO FloodReport (
                Location, AssociatedEmail, AssociatedPhoneNumber, 
                Description, Severity, Verified
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING ID;
            ''',
            (location, email, phone_number, description, severity, 0)
        )

        report_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        print(f"Flood report created with ID: {report_id}")
        return jsonify({"message": "Flood report created", "report_id": report_id}), 201

    except Exception as e:
        print(f"Error creating flood report: {str(e)}")  # Log the exact error
        return jsonify({"error": str(e)}), 500



def get_all_reports():
    """
    Retrieves all flood reports from the database, including verification status.

    Returns:
        flask.Response: A JSON response containing the list of reports or an error message.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Query to fetch all reports including the 'verified' field
        cur.execute(
            '''
            SELECT ID, Location, Severity, AssociatedEmail, Verified
            FROM FloodReport;
            '''
        )

        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Format the response as a list of dictionaries
        reports = [
            {
                "id": row[0],
                "location": row[1],
                "severity": row[2],
                "email": row[3],
                "verified": row[4],  # Add the verified field to the response
            }
            for row in rows
        ]
        return jsonify(reports), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_unverified_reports():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            '''
            SELECT ID, Location, AssociatedEmail, AssociatedPhoneNumber, Description, Severity, LinkToPicture
            FROM FloodReport
            WHERE Verified = 0;
            '''
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        reports = [{"id": row[0], "location": row[1], "email": row[2], "phone": row[3],
                    "description": row[4], "severity": row[5], "picture": row[6]} for row in rows]
        return jsonify(reports), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def verify_report(report_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            '''
            UPDATE FloodReport
            SET Verified = 1
            WHERE ID = %s
            RETURNING ID;
            ''',
            (report_id,)
        )
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if not row:
            return jsonify({"error": "Report not found"}), 404

        return jsonify({"message": "Report verified", "report_id": row[0]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def reject_report(report_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            '''
            UPDATE FloodReport
            SET Verified = 2
            WHERE ID = %s
            RETURNING ID;
            ''',
            (report_id,)
        )
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if not row:
            return jsonify({"error": "Report not found"}), 404

        return jsonify({"message": "Report rejected", "report_id": row[0]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
