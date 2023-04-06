import os
from flask import Flask
from google.cloud.sql.connector import Connector, IPTypes
import pymysql

import sqlalchemy

@app.route('/generatenumbers')
def generate_numbers():
    instance_name = os.environ.get("INSTANCE_NAME", "unknown")

    for _ in range(1000):
        num = random.randint(0, 100000)
        redis_client.lpush("numbers", num)
        redis_client.lpush(f"instance:{instance_name}", num)

    return jsonify({"status": "success", "instance_name": instance_name})


def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of MySQL.

    Uses the Cloud SQL Python Connector package.
    """
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.

    instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"]  # e.g. 'project:region:instance'
    db_user = "rob"  # e.g. 'my-db-user'
    db_pass = "password"  # e.g. 'my-db-password'
    db_name = "numbersdb"  # e.g. 'my-database'

    ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    connector = Connector(ip_type)

    def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        return conn

    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
        # ...
    )
    return pool




