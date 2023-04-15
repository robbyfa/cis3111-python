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

class InstanceCount(Base):
    __tablename__ = "instance_count"

    instance_name = Column(String(255), primary_key=True)
    generated_count = Column(Integer)


# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# Create a session factory
Session = sessionmaker(bind=engine)

@app.route("/generate", methods=["POST"])
@cross_origin(origin="https://cis3111-2023-class.ew.r.appspot.com")
def generate():
    # Get instance ID from environment variables
    instance_id = os.environ.get("GAE_INSTANCE", "unknown-instance")

    numbers_generated = []
    for i in range(1000):
        random_number = random.randint(0, 100000)
        new_entry = NumberEntry(instance_name=instance_id, number=random_number)

        session = Session()
        session.add(new_entry)
        session.commit()

        numbers_generated.append({"instance_name": instance_id, "number": random_number})

    return jsonify(numbers_generated), 201

@app.route("/results", methods=["GET"])
@cross_origin(origin="https://cis3111-2023-class.ew.r.appspot.com")
def get_results():
    session = Session()
    min_number = session.query(NumberEntry).order_by(NumberEntry.number).first()
    max_number = session.query(NumberEntry).order_by(NumberEntry.number.desc()).first()

    return jsonify({
        "min_number": {"instance_name": min_number.instance_name, "number": min_number.number},
        "max_number": {"instance_name": max_number.instance_name, "number": max_number.number}
    }), 200

@app.route("/statistics", methods=["GET"])
@cross_origin(origin="https://cis3111-2023-class.ew.r.appspot.com")
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
@cross_origin(origin="https://cis3111-2023-class.ew.r.appspot.com")
def clear_data():
    session = Session()
    session.query(NumberEntry).delete()
    session.commit()
    return jsonify({"message": "All data cleared"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
