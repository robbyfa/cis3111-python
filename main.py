import random
from flask import Flask, jsonify
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)


# Set up SQLAlchemy engine and session to connect to Cloud SQL database
db_user = 'rob'
db_password = 'stfxv6gvwD+mxP+8JoKnfw2g'
db_name = 'random-numbers'
db_instance_name = 'db-instance'
cloud_sql_connection_name = f'{PROJECT_NAME}:{REGION}:{db_instance_name}'
engine = create_engine(
    f'mysql+pymysql://{db_user}:{db_password}@localhost/{db_name}?unix_socket=/cloudsql/{cloud_sql_connection_name}'
)
Session = sessionmaker(bind=engine)
Base = declarative_base()


# Define ORM model for random numbers table
class RandomNumber(Base):
    __tablename__ = 'random_numbers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(Integer)

# Generate 1,000 random integers between 0 and 100,000 and store them in the database
def generate_random_numbers():
    numbers = [RandomNumber(value=random.randint(0, 100000)) for _ in range(1000)]
    with Session() as session:
        session.add_all(numbers)
        session.commit()

# API endpoint to trigger random number generation and return min/max values
@app.route('/random_numbers')
def get_random_numbers():
    generate_random_numbers()
    with Session() as session:
        numbers = [n.value for n in session.query(RandomNumber).all()]
    return jsonify({
        'min': min(numbers),
        'max': max(numbers)
    })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

