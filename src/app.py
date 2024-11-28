from flask import Flask
import psycopg2

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/db-test')
def db_test():
    try:
        conn = psycopg2.connect(
            dbname="AFM",
            user="afm_user",
            password="afm_password",
            host="db",  # Match the service name in docker-compose.yml
            port=5432
        )
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        result = cur.fetchone()
        conn.close()
        return f"Database connection successful: {result}"
    except Exception as e:
        return f"Database connection failed: {e}"