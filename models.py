import bcrypt
from db_config import execute_query

class User:
    def __init__(self, username, password, role='user'):
        self.username = username
        self.password = self._hash_password(password)
        self.role = role

    def _hash_password(self, password):
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    def verify_password(self, password):
        """Verify a password against the stored hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password)

    def __repr__(self):
        return f"User(username='{self.username}', role='{self.role}')"

    @staticmethod
    def get_by_username(username):
        """Get a user from the database by username."""
        query = "SELECT * FROM users WHERE username = %s"
        result = execute_query(query, (username,), fetch=True)
        if result and len(result) > 0:
            user_data = result[0]
            user = User(user_data['username'], '', user_data['role'])
            user.password = user_data['password']  # Store the hashed password
            return user
        return None

    def save(self):
        """Save or update the user in the database."""
        query = """
            INSERT INTO users (username, password, role, created_at)
            VALUES (%s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE
            password = VALUES(password),
            role = VALUES(role)
        """
        execute_query(query, (self.username, self.password, self.role))

class Admin(User):
    def __init__(self, username, password):
        super().__init__(username, password, 'admin')
        self.users = self.load_users()

    def load_users(self):
        """Load all non-admin users from the database."""
        query = "SELECT * FROM users WHERE role = 'user'"
        result = execute_query(query, fetch=True)
        return [User(user['username'], user['password'], user['role']) for user in result]

    def addUser(self, username, password):
        """Add a new user to the database."""
        new_user = User(username, password, 'user')
        new_user.save()
        self.users = self.load_users()

    def removeUser(self, username):
        """Remove a user from the database."""
        query = "DELETE FROM users WHERE username = %s AND role = 'user'"
        execute_query(query, (username,))
        self.users = self.load_users()

    def addAdmin(self, username):
        """Grant admin privileges to a user."""
        query = "UPDATE users SET role = 'admin' WHERE username = %s"
        execute_query(query, (username,))
        self.users = self.load_users()

    def removeAdmin(self, username):
        """Revoke admin privileges from a user."""
        query = "UPDATE users SET role = 'user' WHERE username = %s"
        execute_query(query, (username,))
        self.users = self.load_users()

    def __repr__(self):
        return f"Admin(username='{self.username}', users={len(self.users)})"
        