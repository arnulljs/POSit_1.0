from models import User, Admin
from db_config import execute_query

# Global list to store users - shared with userManagement.py
_users_list = []

# Session dictionary to store current user info
session = {
    "username": None,
    "role": None
}

def get_users():
    """Returns the list of all users from the database."""
    query = "SELECT * FROM users"
    result = execute_query(query, fetch=True)
    users = []
    for user_data in result:
        user = User(user_data['username'], '', user_data['role'])
        user.password = user_data['password']  # Store the hashed password
        users.append(user)
    return users

def authUser(users: list, username: str, password: str):
    """Authenticate a user against the database."""
    user = User.get_by_username(username)
    if user and user.verify_password(password):
        return user.role
    return None

def setUserSession(username: str, role: str):
    """Set the current user session."""
    session["username"] = username
    session["role"] = role

def getCurrentUser() -> dict:
    """Get the current user session information."""
    return session.copy()

def logout():
    """Clear the current user session."""
    session["username"] = None
    session["role"] = None

def init_default_users():
    """Initialize the database with a default admin user if none exists."""
    query = "SELECT id FROM users WHERE username = 'admin'"
    result = execute_query(query, fetch=True)
    
    if not result:
        # Create default admin user
        admin = Admin("admin", "admin123")
        admin.save()

# Call this when the app starts
init_default_users()