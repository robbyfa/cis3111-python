import os
import random
from flask import Flask, jsonify
import mysql.connector
from google.cloud.sql.connector import connector

app = Flask(__name__)

CLOUD_SQL_PASSWORD = "W7Kjjw+Xe9iaW008m1w0UsOq"
PROJECT_ID = "numbers-generator-assignment"
DB_INSTANCE_NAME = "db-instance"
DB_NAME = "numbers"
DB_USER = "rob"
REGION = "europe-west1"

def connect_to_cloudsql():
    connection_string = {
        "user": DB_USER,
        "password": CLOUD_SQL_PASSWORD,
        "host": f"{PROJECT_ID}:{REGION}:{DB_INSTANCE_NAME}",
        "database": DB_NAME,
    }
    connection = connector.connect(connection_string, "cloudsql")
    return connection

@app.route("/generate_numbers")
def generate_numbers():
    connection = connect_to_cloudsql()
    cursor = connection.cursor()

    instance_name = os.getenv("GAE_INSTANCE")

    for _ in range(1000):
        random_number = random.randint(0, 100000)
        cursor.execute("INSERT INTO random_numbers (instance_name, number) VALUES (%s, %s)", (instance_name, random_number))

    connection.commit()
    cursor.close()
    connection.close()
    
    return jsonify({"status": "success"})

@app.route("/get_results")
def get_results():
    connection = connect_to_cloudsql()
    cursor = connection.cursor()

    cursor.execute("SELECT instance_name, COUNT(*) FROM random_numbers GROUP BY instance_name")
    instance_counts = cursor.fetchall()

    cursor.execute("SELECT instance_name, MIN(number) FROM random_numbers")
    smallest_number = cursor.fetchone()

    cursor.execute("SELECT instance_name, MAX(number) FROM random_numbers")
    largest_number = cursor.fetchone()

    cursor.close()
    connection.close()

    return jsonify({
        "instance_counts": instance_counts,
        "smallest_number": smallest_number,
        "largest_number": largest_number
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
