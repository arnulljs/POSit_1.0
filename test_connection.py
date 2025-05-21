import mysql.connector
from mysql.connector import Error
import time

def test_connection():
    try:
        print("Attempting to connect to the database...")
        connection = mysql.connector.connect(
            host='sql12.freesqldatabase.com',
            user='sql12780094',
            password='d293VM7qBK',
            database='sql12780094',
            port=3306,
            connect_timeout=10,  # Add timeout
            use_pure=True  # Use pure Python implementation
        )
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Connected to MySQL Server version {db_info}")
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()[0]
            print(f"Connected to database: {db_name}")
            
            # Test a simple query
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print("\nAvailable tables:")
            for table in tables:
                print(f"- {table[0]}")
            
            cursor.close()
            print("\nConnection test successful!")
            
    except Error as e:
        print(f"\nError during connection test:")
        print(f"Error Code: {e.errno}")
        print(f"Error Message: {e.msg}")
        if hasattr(e, 'sqlstate'):
            print(f"SQL State: {e.sqlstate}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    test_connection() 