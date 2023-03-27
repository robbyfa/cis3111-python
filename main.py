from flask import Flask, jsonify
from google.cloud import sqlconnector
import os
import random

app = Flask(__name__)

CLOUD_SQL_CONNECTION_NAME = os.environ.get("CLOUD_SQL_CONNECTION_NAME")
CLOUD_SQL_USER = os.environ.get("DB_USER")
CLOUD_SQL_PASSWORD = os.environ.get("CLOUD_SQL_PASSWORD")
CLOUD_SQL_DATABASE = os.environ.get("DB_NAME")

db = sqlconnector.connect(
    unix_socket = f"/cloudsql/{CLOUD_SQL_CONNECTION_NAME}",
    user = CLOUD_SQL_USER,
    password = CLOUD_SQL_PASSWORD,
    database = CLOUD_SQL_DATABASE
)

def create_table():
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS random_numbers (
            id SERIAL NOT NULL PRIMARY KEY,
            instance_name VARCHAR(255) NOT NULL,
            number INTEGER NOT NULL
        )
    """)
    db.commit()

def insert_number(instance_name, number):
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO random_numbers (instance_name, number)
        VALUES (%s, %s)
    """, (instance_name, number))
    db.commit()

def get_numbers():
    cursor = db.cursor()
    cursor.execute("""
        SELECT instance_name, number FROM random_numbers
    """)
    results = cursor.fetchall()
    return results

@app.route('/generate')
def generate_numbers():
    instance_name = os.environ.get("GAE_INSTANCE")
    for i in range(1000):
        number = random.randint(0, 100000)
        insert_number(instance_name, number)
    return "Numbers generated and stored in the database."

@app.route('/get_results')
def get_results():
    numbers = get_numbers()
    results = {
        "total_numbers": len(numbers),
        "numbers_by_instance": {}
    }
    for instance_name, number in numbers:
        if instance_name not in results["numbers_by_instance"]:
            results["numbers_by_instance"][instance_name] = 0
        results["numbers_by_instance"][instance_name] += 1
    results["largest_number"] = max(numbers, key=lambda x: x[1])
    results["smallest_number"] = min(numbers, key=lambda x: x[1])
    return jsonify(results)

if __name__ == '__main__':
    create_table()
    app.run(host='127.0.0.1', port=8080, debug=True)
