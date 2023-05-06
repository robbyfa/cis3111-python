from flask import Flask, jsonify, request
from google.cloud.sql.connector import Connector
import pymysql
import random
import os
import re
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "https://cis3111-2023-class.ew.r.appspot.com"}})

# Create database engine
db_user = "rob"
db_pass = "uWzKUp8YtnLuRqJP/dbeZLdV"
db_name = "numbersdb"
db_socket_dir = "/cloudsql"
cloud_sql_instance_name = "cis3111-2023-class:europe-west1:db-instance"

db_url = f"mysql+pymysql://{db_user}:{db_pass}@/{db_name}?unix_socket={db_socket_dir}/{cloud_sql_instance_name}"
engine = create_engine(db_url)

# Define your database model
Base = declarative_base()

class NumberEntry(Base):
    __tablename__ = "numbers"

    id = Column(Integer, primary_key=True)
    instance_name = Column(String(255))
    number = Column(Integer)



class InstanceCounter(Base):
    __tablename__ = "instance_counters"

    id = Column(Integer, primary_key=True)
    instance_name = Column(String(255))
    count = Column(Integer)

# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# Create a session factory
Session = sessionmaker(bind=engine)


Base.metadata.create_all(engine)

@app.route("/generate", methods=["POST"])
def generate():
    # Get instance ID from environment variables
    instance_id = os.environ.get("GAE_INSTANCE", "unknown-instance")

    # Extract instance number from instance_id using a regular expression
    instance_number_match = re.search(r'\d+', instance_id)
    if instance_number_match:
        instance_number = int(instance_number_match.group())
    else:
        instance_number = 0

    # Retrieve or create a counter for the instance
    session = Session()
    instance_counter = session.query(InstanceCounter).filter(InstanceCounter.instance_name == f"Instance {instance_number}").one_or_none()
    
    if not instance_counter:
        instance_counter = InstanceCounter(instance_name=f"Instance {instance_number}", count=0)
        session.add(instance_counter)
        session.commit()

    # Check if the instance has already generated 1000 numbers
    if instance_counter.count >= 1000:
        return jsonify({"error": "This instance has already generated 1000 numbers."}), 400

    numbers_generated = []
    for i in range(1000):
        random_number = random.randint(0, 100000)
        new_entry = NumberEntry(instance_name=f"Instance {instance_number}", number=random_number)

        session = Session()
        session.add(new_entry)
        session.commit()

        # Update the counter
        instance_counter.count += 1
        session.add(instance_counter)
        session.commit()

        numbers_generated.append({"instance_name": f"Instance {instance_number}", "number": random_number})

    return jsonify(numbers_generated), 201, {'Access-Control-Allow-Origin': '*'}
@app.route("/results", methods=["GET"])
def get_results():
    session = Session()
    min_number = session.query(NumberEntry).order_by(NumberEntry.number).first()
    max_number = session.query(NumberEntry).order_by(NumberEntry.number.desc()).first()

    return jsonify({
        "min_number": {"instance_name": min_number.instance_name, "number": min_number.number},
        "max_number": {"instance_name": max_number.instance_name, "number": max_number.number}
    }), 200

@app.route("/statistics", methods=["GET"])
def get_statistics():
    session = Session()
    query = session.query(
        NumberEntry.instance_name,
        func.count(NumberEntry.number).label("total_numbers"),
        func.max(NumberEntry.number).label("max_number"),
        func.min(NumberEntry.number).label("min_number")
    ).group_by(NumberEntry.instance_name).all()

    statistics = [
        {
            "instance_name": row[0],
            "total_numbers": row[1],
            "max_number": row[2],
            "min_number": row[3]
        } for row in query
    ]

    return jsonify(statistics), 200, {'Access-Control-Allow-Origin': '*'}

@app.route("/clear", methods=["POST"])
def clear_data():
    session = Session()
    session.query(NumberEntry).delete()
    session.commit()
    return jsonify({"message": "All data cleared"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
