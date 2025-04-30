session = {
    "username": None,
    "role": None   
}

def authUser(users: list, username: str, password: str):
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