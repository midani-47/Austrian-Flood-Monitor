from flask import Flask, render_template
import psycopg2
from .model.report_model import create_flood_report

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


#
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
