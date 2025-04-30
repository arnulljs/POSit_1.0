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
from kivy.uix.screenmanager import ScreenManager, Screen
from loginGUI import LoginScreen
from models import User, Admin
from userGUI import MainScreen  # Import the MainScreen from userGUI.py

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="Home Screen"))
        layout.add_widget(Button(text="Logout", on_press=self.logout))
        self.add_widget(layout)

    def logout(self, instance):
        import auth
        auth.logout()
        self.manager.current = "login"

class POSitApp(App):
    def build(self):
        # create users
        user1 = User("bro", "bruhh", "user")
        user2 = User("cro", "lolz", "user")
        admin = Admin("tro", "what")
        admin.addUser(user1)
        admin.addUser(user2)

        sm = ScreenManager()
        sm.add_widget(LoginScreen(users=admin.users, name="login"))
        
        # Use the MainScreen from userGUI.py after login instead of HomeScreen
        sm.add_widget(MainScreen(name="home"))  # Redirect to MainScreen from userGUI.py
        
        return sm

if __name__ == '__main__':
    POSitApp().run()
