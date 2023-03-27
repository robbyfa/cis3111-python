# Import required libraries
import os
import random
from flask import Flask, request, jsonify
from google.cloud import sqlconnector

# Initialize Flask app
app = Flask(__name__)

# Configure Cloud SQL
PASSWORD = os.environ["CLOUD_SQL_PASSWORD"]
INSTANCE_NAME = os.environ["DB_INSTANCE_NAME"]
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]

# Create Cloud SQL client
def init_sql():
    db_config = {
        "user": DB_USER,
        "password": PASSWORD,
        "host": f"/cloudsql/{INSTANCE_NAME}",
        "database": DB_NAME
    }
    conn = sqlconnector.connect(**db_config)
    return conn

# Generate random numbers and store in Cloud SQL
@app.route("/generate_numbers", methods=["POST"])
def generate_numbers():
    # Generate 1000 random numbers
    numbers = [random.randint(0, 100000) for _ in range(1000)]

    # Store numbers in Cloud SQL
    conn = init_sql()
    cursor = conn.cursor()
    for num in numbers:
        query = f"INSERT INTO random_numbers (number) VALUES ({num})"
        cursor.execute(query)
    conn.commit()

    # Return success message
    return jsonify({"message": "Random numbers generated and stored in Cloud SQL"})

# Retrieve smallest and largest numbers from Cloud SQL
@app.route("/get_extremes", methods=["GET"])
def get_extremes():
    # Retrieve smallest and largest numbers from Cloud SQL
    conn = init_sql()
    cursor = conn.cursor()
    cursor.execute("SELECT MIN(number), MAX(number) FROM random_numbers")
    result = cursor.fetchone()

    # Format result
    min_num = result[0]
    max_num = result[1]
    response = {
        "smallest_number": min_num,
        "largest_number": max_num
    }

    # Return result
    return jsonify(response)
