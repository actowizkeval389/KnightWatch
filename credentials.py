from dotenv import load_dotenv
import os
import pymysql

# Load environment variables from the .env file
load_dotenv()

def get_db_connection():
    # Fetch database credentials from environment variables
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_NAME")

    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor
    )
