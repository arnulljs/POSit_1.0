import mysql.connector
from db_config import DB_CONFIG
import bcrypt

def hash_passwords():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, password FROM users")
    users = cursor.fetchall()
    for user in users:
        # Skip if already hashed
        if isinstance(user['password'], str) and user['password'].startswith('$2b$'):
            print(f"User {user['username']} already hashed, skipping.")
            continue
        password = user['password']
        if isinstance(password, bytes):
            password = password.decode('utf-8')
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, user['id']))
        print(f"Updated password for user {user['username']}")
    conn.commit()
    cursor.close()
    conn.close()
    print("All passwords hashed.")

if __name__ == "__main__":
    hash_passwords() 