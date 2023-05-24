from flask import Flask, jsonify, request, make_response
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
CORS(app, resources={r"*": {"origins": ["https://cis3111-2023-class.ew.r.appspot.com"]}})

# Create database engine
db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASSWORD")
db_name = os.environ.get("DB_NAME")
cloud_sql_instance_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")
db_socket_dir = "/cloudsql"

db_url = f"mysql+pymysql://{db_user}:{db_pass}@/{db_name}?unix_socket={db_socket_dir}/{cloud_sql_instance_name}"
engine = create_engine(db_url)

# Define database model
Base = declarative_base()

class NumberEntry(Base):
    __tablename__ = "numbers"

    id = Column(Integer, primary_key=True)
    instance_name = Column(String(255))
    number = Column(Integer)


# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# Create session factory
Session = sessionmaker(bind=engine)


Base.metadata.create_all(engine)

@app.route("/generate", methods=["POST"])
def generate():
  
    numbers_generated = []
    for i in range(1000):
        instance_id = os.environ.get("GAE_INSTANCE", "unknown-instance")
        random_number = random.randint(0, 100000)
        new_entry = NumberEntry(instance_name=f"Instance {instance_id[-5:]}", number=random_number)
        session = Session()
        session.add(new_entry)
        session.commit()


        numbers_generated.append({"instance_name": f"Instance {instance_id}", "number": random_number})

    response = make_response(jsonify(numbers_generated), 201)
    response.headers['Access-Control-Allow-Origin'] = 'https://cis3111-2023-class.ew.r.appspot.com'
    return response

@app.route("/results", methods=["GET"])
def get_results():
    session = Session()
    min_number = session.query(NumberEntry).order_by(NumberEntry.number).first()
    max_number = session.query(NumberEntry).order_by(NumberEntry.number.desc()).first()

    response = make_response(jsonify({
        "min_number": {"instance_name": min_number.instance_name, "number": min_number.number},
        "max_number": {"instance_name": max_number.instance_name, "number": max_number.number}
    }), 200)
    response.headers['Access-Control-Allow-Origin'] = 'https://cis3111-2023-class.ew.r.appspot.com'
    return response

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

    response = make_response(jsonify(statistics), 200)
    response.headers['Access-Control-Allow-Origin'] = 'https://cis3111-2023-class.ew.r.appspot.com'
    return response

@app.route("/clear", methods=["POST"])
def clear_data():
    session = Session()
    session.query(NumberEntry).delete()
    session.commit()

    response = make_response(jsonify({"message": "All data cleared"}), 200)
    response.headers['Access-Control-Allow-Origin'] = 'https://cis3111-2023-class.ew.r.appspot.com'
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)