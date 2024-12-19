import logging
import os
import pyodbc
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

logging.basicConfig(filename='db_connection.log', level=logging.DEBUG)


# Get the DATABASE_URL from the .env file
conn_str = os.getenv("SQLALCHEMY_DATABASE_URI")


# Create the SQLAlchemy engine
engine = create_engine(conn_str)

# Test the connection
try:
    connection = engine.connect()
    print("Connection successful!")
    connection.close()
except Exception as e:
    print("Error:", e)