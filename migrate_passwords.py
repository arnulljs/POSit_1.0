import mysql.connector
from db_config import DB_CONFIG
import bcrypt

def migrate_passwords():
    try:
        # Connect to the database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 1. Check if password column is BLOB, if not alter it
        cursor.execute("SHOW COLUMNS FROM users WHERE Field = 'password'")
        password_column = cursor.fetchone()
        if password_column and password_column['Type'] != 'BLOB':
            print("Converting password column to BLOB type...")
            cursor.execute("ALTER TABLE users MODIFY COLUMN password BLOB NOT NULL")
        
        # 2. Check if timestamp columns exist, add if they don't
        cursor.execute("SHOW COLUMNS FROM users WHERE Field = 'created_at'")
        if not cursor.fetchone():
            print("Adding created_at column...")
            cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        
        cursor.execute("SHOW COLUMNS FROM users WHERE Field = 'updated_at'")
        if not cursor.fetchone():
            print("Adding updated_at column...")
            cursor.execute("ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
        
        # 3. Get all users and update their passwords to be hashed
        cursor.execute("SELECT id, username, password FROM users")
        users = cursor.fetchall()
        
        for user in users:
            # Skip if password is already hashed (bcrypt hashes start with $2b$)
            if isinstance(user['password'], bytes) and user['password'].startswith(b'$2b$'):
                print(f"Password for user {user['username']} is already hashed, skipping...")
                continue
            
            # Hash the password
            password = user['password'].decode('utf-8') if isinstance(user['password'], bytes) else user['password']
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Update the user's password
            cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, user['id']))
            print(f"Updated password for user {user['username']}")
        
        # Commit the changes
        conn.commit()
        print("Migration completed successfully!")
        
    except mysql.connector.Error as err:
        print(f"Error during migration: {err}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate_passwords() 