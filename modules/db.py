import sqlite3
from .logger import logger
import os

#Function to connect to the db
def create_connection(db_file):
    """ Create a database connection to a SQLite database """
    logger.debug("connecting to database")
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
    return conn

# Funtion to 
def setup_database():
    """ Setup or connect to an existing database and create table if not exists """
    logger.info("Setting up database")
    db_path = 'db/request_times.db'
    os.makedirs(os.path.dirname(db_path), exist_ok=True)  # Ensure the db directory exists

    conn = create_connection(db_path)
    if conn is not None:
        create_table_sql = '''
        CREATE TABLE IF NOT EXISTS requests (
            email TEXT NOT NULL,
            last_request_time REAL NOT NULL
        );
        '''
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except Exception as e:
            logger.error(f"Error creating table: {str(e)}")
        finally:
            conn.close()

def get_last_request_time(email):
    """ Get the last request time of the user """
    logger.debug(f"checking last request time for {email}")
    db_path = 'db/request_times.db'
    conn = create_connection(db_path)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT last_request_time FROM requests WHERE email = ?", (email,))
        result = cur.fetchone()
        if result:
            return result[0]
    return None

def update_last_request_time(email, time_stamp):
    """ Update the last request time of the user """
    logger.debug(f"setting last request time for {email} to {time_stamp}")
    db_path = 'db/request_times.db'
    conn = create_connection(db_path)
    with conn:
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO requests (email, last_request_time) VALUES (?, ?)", (email, time_stamp))
        conn.commit()