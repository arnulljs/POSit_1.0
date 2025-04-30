class User:
    def __init__(self, username: str, hashPass: str, role: str):
        self.username = username
        self.hashPass = hashPass
        self.role = role
    def __repr__(self):
        return f"User(username={self.username}, role={self.role})"
        
        
class Admin(User):
    def __init__(self, username: str, hashPass: str):
        super().__init__(username, hashPass, role="admin")
        self.users = []
        
    def addUser(self, user: User):
        self.users.append(user)
        
    def removeUser(self, username: str):
        self.users = [user for user in self.users if user.username != username]
        
    def addAdmin(self, username: str):
         for user in self.users:
            if user.username == username:
                user.role = "admin"
                print(f"\nAdmin privileges added to {username}")
                break
            else:
                print(f"User {username} not found.")
    
    def removeAdmin(self, username: str):
        for user in self.users:
            if user.username == username:
                user.role = "user"
                print(f"\nAdmin privileges removed from {username}")
                break
            else:
                print(f"User {username} not found.")
                
    def __repr__(self):
        return f"Admin(username={self.username}, role={self.role}, users={self.users})"
        