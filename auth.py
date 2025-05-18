from models import User, Admin

# Global list to store users - shared with userManagement.py
_users_list = []

# Session dictionary to store current user info
session = {
    "username": None,
    "role": None
}

def get_users():
    """Returns the list of all users."""
    return _users_list

def authUser(users: list, username: str, password: str):
    # First check the global users list
    for user in _users_list:
        if user.username == username and user.hashPass == password:
            return user.role
    
    # Then check the passed users list (for backward compatibility)
    for user in users:
        if user.username == username and user.hashPass == password:
            return user.role
    return None

def setUserSession(username: str, role: str):
    session["username"] = username
    session["role"] = role
    
def logout():
    session["username"] = None
    session["role"] = None

def getCurrentUser() -> dict:
    return session.copy()

# Initialize with some default users
def init_default_users():
    global _users_list
    if not _users_list:  # Only add if list is empty
        _users_list.extend([
            Admin("admin", "admin123"),  # Admin class automatically sets role to "admin"
            User("user", "user123", "user")  # User class needs role specified
        ])

# Call this when the app starts
init_default_users()