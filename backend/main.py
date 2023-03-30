from flask import Flask, jsonify, request
import psycopg2
import os
import random

app = Flask(__name__)

# Define database configuration
db_config = {
    "user": "rob",
    "password": os.environ["CLOUD_SQL_PASSWORD"],
    "host": "random-numbers-assignment:europe-west1",
    "database": "numbers",
    "unix_socket": f"/cloudsql/{os.environ['PROJECT_NAME']}:europe-west1:db-instance",
}

# Define API endpoints
@app.route('/generate', methods=['POST'])
def generate_numbers():
    # Generate random numbers
    numbers = [random.randint(0, 100000) for _ in range(1000)]
    # Store numbers in database
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    for num in numbers:
        cur.execute("INSERT INTO numbers (num) VALUES (%s)", (num,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'Numbers generated successfully'})

@app.route('/results', methods=['GET'])
def get_results():
    # Retrieve largest and smallest numbers
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute("SELECT MAX(num), MIN(num) FROM numbers")
    result = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify({'largest': result[0], 'smallest': result[1]})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
