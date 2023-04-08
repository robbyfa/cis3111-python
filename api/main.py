from flask import Flask, jsonify, request
from google.cloud.sql.connector import Connector
import pymysql
import random
import os
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
CORS(app)

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

class InstanceCount(Base):
    __tablename__ = "instance_count"

    instance_name = Column(String(255), primary_key=True)
    generated_count = Column(Integer)


# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# Create a session factory
Session = sessionmaker(bind=engine)

@app.route("/generate", methods=["POST"])
def generate():
    instance_name = request.form.get("instance_name")

    session = Session()
    
    # Check if the current instance has an entry in the instance_count table
    instance_entry = session.query(InstanceCount).filter_by(instance_name=instance_name).one_or_none()
    
    if instance_entry is None:
        # If no entry exists, create a new one with count 0
        instance_entry = InstanceCount(instance_name=instance_name, generated_count=0)
        session.add(instance_entry)
        session.commit()

    # Check if the current instance has generated 1000 numbers
    if instance_entry.generated_count >= 1000:
        # Use a new instance for the next batch of numbers
        instance_name = f"Instance {int(instance_name.split(' ')[1]) + 1}"

    numbers_generated = []
    for _ in range(1000):
        random_number = random.randint(0, 100000)
        new_entry = NumberEntry(instance_name=instance_name, number=random_number)

        session.add(new_entry)
        
        numbers_generated.append({"instance_name": instance_name, "number": random_number})

    # Increment the generated_count for the current instance
    instance_entry.generated_count += 1000
    session.commit()

    return jsonify(numbers_generated), 201


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
