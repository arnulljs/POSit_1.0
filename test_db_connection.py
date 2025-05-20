from db_config import get_db_connection, close_db_connection

def test_connection():
    try:
        print("Attempting to connect to the database...")
        connection = get_db_connection()
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Connected to MySQL Server version {db_info}")
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()[0]
            print(f"Connected to database: {db_name}")
            cursor.close()
            print("Connection test successful!")
    except Exception as e:
        print(f"Error during connection test: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            close_db_connection(connection)
            print("Database connection closed.")

if __name__ == "__main__":
    test_connection() 