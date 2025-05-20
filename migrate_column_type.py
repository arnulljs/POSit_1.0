import mysql.connector
from db_config import DB_CONFIG

def migrate_column_type():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users MODIFY COLUMN password VARCHAR(100) NOT NULL")
        conn.commit()
        print("Column type changed successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate_column_type() 