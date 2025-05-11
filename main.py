'''from models import User, Admin
import auth

user1 = User("bro", "bruhh", "user")
user2 = User("cro", "lolz", "user")
admin = Admin("tro", "what")

admin.addUser(user1)
admin.addUser(user2)

print("Adding admin: ")
admin.addAdmin("bro")
print("\n",admin)

admin.removeAdmin("bro")
print("\n\nAfter removing admin: ")
print("\n",admin)

admin.removeUser("cro")

print("\n\nAfter removing user: ")
print("\n",admin)

print("Login test: ")
username = input("Username: ")
password = input("Password: ")

role = auth.authUser(admin.users, username, password)
if role:
    auth.setUserSession(username, role)
    print(f"\nLogin successful. Logged in as {role}")
else:
    print("\nLogin failed.")
    
print("Current Session: ", auth.getCurrentUser())'''

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from loginGUI import LoginScreen
from models import User, Admin
from userGUI import MainScreen
from adminDashGUI import AdminDashboard
import traceback
from kivy.core.window import Window
import adminNav

class POSitApp(App):
    def build(self):
        try:
            print("Starting app initialization...")
            # Set window size for desktop
            Window.size = (1280, 720)
            Window.minimum_width, Window.minimum_height = 1024, 680
            
            # create users
            user1 = User("bro", "bruhh", "admin") #bro is now an admin role and will redirect to admin dashboard
            user2 = User("cro", "lolz", "user") #cro is a user role and will redirect to user dashboard
            admin = Admin("tro", "what")
            admin.addUser(user1)
            admin.addUser(user2)
            print("Users created successfully")

            sm = ScreenManager()
            print("Creating login screen...")
            sm.add_widget(LoginScreen(users=admin.users, name="login"))
            
            sm.add_widget(MainScreen(name="user_dashboard"))
            sm.add_widget(AdminDashboard(name="admin_dashboard"))
            
            print("All screens created successfully")
            return sm
        except Exception as e:
            print("Error during app initialization:")
            print(traceback.format_exc())
            raise

if __name__ == '__main__':
    try:
        print("Starting POSitApp...")
        POSitApp().run()
    except Exception as e:
        print("Fatal error in app:")
        print(traceback.format_exc())
        input("Press Enter to exit...")  # This will keep the window open to see the error
