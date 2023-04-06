from flask import Flask, jsonify, request
from google.cloud.sql.connector import Connector
import pymysql
import random
import os
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String
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

# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# Create a session factory
Session = sessionmaker(bind=engine)

@app.route("/generate", methods=["POST"])
def generate():
    instance_name = request.form.get("instance_name")

    numbers_generated = []
    for i in range(10):
        for j in range(1000):
            random_number = random.randint(0, 100000)
            new_entry = NumberEntry(instance_name=instance_name, number=random_number)

            session = Session()
            session.add(new_entry)
            session.commit()

            numbers_generated.append({"instance_name": instance_name, "number": random_number})

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


@app.route("/instances", methods=["GET"])
def get_instances():
    session = Session()
    query = session.query(NumberEntry.instance_name, func.count(NumberEntry.instance_name)).group_by(NumberEntry.instance_name).all()

    instance_counts = [{"instance_name": row[0], "count": row[1]} for row in query]

    return jsonify(instance_counts), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
