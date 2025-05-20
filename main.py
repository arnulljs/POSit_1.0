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
from kivy.core.window import Window
from kivy.metrics import dp

from loginGUI import LoginScreen
from adminDashGUI import AdminDashboard
from userGUI import MainScreen
from models import User, Admin
import auth

class POSitApp(App):
    def build(self):
        # Set window size
        Window.size = (1200, 800)
        Window.minimum_width = 1000
        Window.minimum_height = 600

        # Create screen manager
        sm = ScreenManager()

        # Initialize default admin user if not exists
        auth.init_default_users()

        # Get users from database
        users = auth.get_users()

        # Add screens
        sm.add_widget(LoginScreen(users=users, name='login'))
        sm.add_widget(AdminDashboard(name='admin_dashboard'))
        sm.add_widget(MainScreen(name='user_dashboard'))

        return sm

if __name__ == '__main__':
    POSitApp().run()
        