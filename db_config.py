import mysql.connector
from mysql.connector import Error

# Database configuration
DB_CONFIG = {
    'host': 'sql12.freesqldatabase.com',
    'user': 'sql12780094',
    'password': 'd293VM7qBK',
    'database': 'sql12780094',
    'port': 3306
}

def get_db_connection():
    """Create and return a database connection."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL database: {err}")
        raise

def close_db_connection(connection):
    """Close the database connection."""
    if connection and connection.is_connected():
        connection.close()

def execute_query(query, params=None, fetch=False):
    """Execute a database query and optionally fetch results."""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        if fetch:
            result = cursor.fetchall()
        else:
            connection.commit()
            result = None
            
        cursor.close()
        return result
    except Exception as e:
        print(f"Database error: {e}")
        raise
    finally:
        if connection:
            close_db_connection(connection) 