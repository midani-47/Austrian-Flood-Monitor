import psycopg2
from flask import jsonify, request

#todo:
# emergency services permission level: 3


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

# Function to create a new dispatch
def create_emergency_dispatch():
    """
    Handles the creation of an emergency dispatch.

    Extracts the Report ID from the JSON body of an HTTP POST request
    and inserts a new emergency dispatch into the `EmergencyResponse` table.

    Returns:
        flask.Response: A JSON response indicating success or failure of the operation.
    """
    data = request.json

    # Validate mandatory fields
    report_id = data.get('report_id')
    if not report_id:
        return jsonify({"error": "Report ID is mandatory"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert into EmergencyResponse table
        cur.execute(
            '''
            INSERT INTO EmergencyResponse (ReportID)
            VALUES (%s)
            RETURNING ID, Status;
            ''',
            (report_id,)
        )

        dispatch_id, status = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Emergency dispatch created", "dispatch_id": dispatch_id, "status": status}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Function to get all dispatches for a report
def get_dispatches_by_report(report_id):
    """
    Retrieves all emergency dispatches associated with a given report.

    Args:
        report_id (int): The ID of the report.

    Returns:
        flask.Response: A JSON response containing the dispatches or an error message.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Query dispatches for the given ReportID
        cur.execute(
            '''
            SELECT ID, Status, ReportID
            FROM EmergencyResponse
            WHERE ReportID = %s;
            ''',
            (report_id,)
        )

        rows = cur.fetchall()
        cur.close()
        conn.close()

        if not rows:
            return jsonify({"error": "No dispatches found for this report"}), 404

        # Format the response
        dispatches = [{"ID": row[0], "Status": row[1], "ReportID": row[2]} for row in rows]
        return jsonify(dispatches), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Function to update the status of a dispatch
def update_dispatch_status(dispatch_id):
    """
    Updates the status of an emergency dispatch.

    Args:
        dispatch_id (int): The ID of the dispatch to update.

    Returns:
        flask.Response: A JSON response indicating success or failure of the operation.
    """
    data = request.json

    # Validate new status
    new_status = data.get('status')
    valid_statuses = ["Planning", "on the way", "operation in progress", "operation completed"]
    if new_status not in valid_statuses:
        return jsonify({"error": "Invalid status"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Update the status in the EmergencyResponse table
        cur.execute(
            '''
            UPDATE EmergencyResponse
            SET Status = %s
            WHERE ID = %s
            RETURNING ID, Status;
            ''',
            (new_status, dispatch_id)
        )

        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if not row:
            return jsonify({"error": "Dispatch not found"}), 404

        return jsonify({"message": "Dispatch status updated", "dispatch_id": row[0], "new_status": row[1]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500