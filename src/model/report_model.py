import psycopg2
import random
from flask import jsonify, request

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

    Extracts data from the JSON body of an HTTP POST request, validates required fields,
    and inserts the data into the `FloodReport` table. The function generates a random
    placeholder for the `Location` field.

    Returns:
        flask.Response: A JSON response indicating success or failure of the operation.
    """

    data = request.json

    # Validate mandatory fields
    email = data.get('email').strip().lower()
    severity = data.get('severity')
    if not email or not severity:
        return jsonify({"error": "Email and severity are mandatory"}), 400
    
    locationOn = data.get('location')

    if(locationOn):
        # Get Data from JSON latitude then longitutde
        location = f"{data.get('lat')},{data.get('long')}"
    else:
        # Generate random location placeholder
        location = f"{random.uniform(47.065415, 48.471273):.6f},{random.uniform(13.073759, 16.372826):.6f}" # todo: could also just do "random location"
        #city locations:
        # Vienna: ~48.213568 16.372826
        # St Pölten: ~48.202119 15.634828
        # Graz: ~47.065415 15.42632
        # Salzburg: ~47.805343 13.073759
        #
        # min lat: 47.065415, max lat: 48.471273
        # min long: 13.073759, max long: 16.372826
        #

    # Optional fields
    phone_number = data.get('phone_number')
    user_id = data.get('user_id')
    description = data.get('description')
    picture = data.get('picture')  # Assume this is a URL or file path TODO: this has to be fixed later

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert into database
        cur.execute(
            '''
            INSERT INTO FloodReport (Location, AssociatedEmail, AssociatedPhoneNumber, AssociatedUserID, 
                                      Description, LinkToPicture, Severity, Verified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING ID;
            ''',
            (location, email, phone_number, user_id, description, picture, severity, False)
        )

        report_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Flood report created", "report_id": report_id}), 201

    except Exception as e:
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
