from flask import Flask, jsonify, request
from google.cloud import sqlconnector

app = Flask(__name__)

# Initialize the SQL connection pool
db_user = "rob"
db_pass = "YFDH7aB9i0f6gNhkDaztTqjQ"
db_name = "random-numbers"
db_socket_dir = "/cloudsql"
cloud_sql_connection_name = "CIS3111-assignment:europe-west1:db-instance"
db_pool = sqlconnector.connect(
    user=db_user,
    password=db_pass,
    unix_socket=f"{db_socket_dir}/{cloud_sql_connection_name}/{db_name}"
)

# API endpoint for generating and storing random numbers
@app.route("/generate", methods=["POST"])
def generate_random_numbers():
    # Get the number of random numbers to generate from the request
    num_numbers = request.json.get("num_numbers", 1000)
    
    # Generate the random numbers
    random_numbers = [random.randint(0, 100000) for i in range(num_numbers)]
    
    # Store the random numbers in the database
    with db_pool.cursor() as cursor:
        insert_query = "INSERT INTO random_numbers (number) VALUES (%s)"
        values = [(num,) for num in random_numbers]
        cursor.executemany(insert_query, values)
        db_pool.commit()
    
    # Return a success message
    return jsonify({"message": f"Generated and stored {num_numbers} random numbers"})


# API endpoint for retrieving the largest and smallest random numbers
@app.route("/results", methods=["GET"])
def get_random_number_results():
    # Retrieve the largest and smallest random numbers from the database
    with db_pool.cursor() as cursor:
        select_query = "SELECT MAX(number), MIN(number) FROM random_numbers"
        cursor.execute(select_query)
        results = cursor.fetchone()
    
    # Format the results as a JSON object and return it
    return jsonify({
        "largest": results[0],
        "smallest": results[1]
    })


if __name__ == "__main__":
    app.run()
