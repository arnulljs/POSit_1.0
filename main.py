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
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from loginGUI import LoginScreen
from adminDashGUI import AdminDashboard
from userGUI import MainScreen
from adminInventory import AdminInventoryScreen
from userManagement import UserManagementScreen
from reportsGUI import ReportScreen
from models import User, Admin
import auth

class CachedScreenManager(ScreenManager):
    """A ScreenManager that caches screen instances."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._screen_cache = {}
        self._screen_constructors = {
            'login': lambda: LoginScreen(users=auth.get_users(), name='login'),
            'admin_dashboard': lambda: AdminDashboard(name='admin_dashboard'),
            'user_dashboard': lambda: MainScreen(name='user_dashboard'),
            'admin_inventory': lambda: AdminInventoryScreen(name='admin_inventory'),
            'user_management': lambda: UserManagementScreen(name='user_management'),
            'reports_screen': lambda: ReportScreen(name='reports_screen')
        }
        
        # Pre-initialize the login screen since it's the first screen
        self._initialize_screen('login')
    
    def _initialize_screen(self, screen_name):
        """Initialize a screen if it hasn't been created yet."""
        if screen_name not in self._screen_cache:
            screen = self._screen_constructors[screen_name]()
            self._screen_cache[screen_name] = screen
            self.add_widget(screen)
    
    def switch_to(self, screen_name):
        """Switch to a screen, initializing it if necessary."""
        self._initialize_screen(screen_name)
        self.current = screen_name
    
    def get_screen(self, screen_name):
        """Get a screen instance, initializing it if necessary."""
        self._initialize_screen(screen_name)
        return self._screen_cache[screen_name]

class POSitApp(App):
    def build(self):
        # Set window size
        Window.size = (1200, 800)
        Window.minimum_width = 1000
        Window.minimum_height = 600

        # Initialize default admin user if not exists
        auth.init_default_users()

        # Create screen manager with caching
        sm = CachedScreenManager()
        
        # The login screen will be automatically initialized
        # Other screens will be initialized on demand
        
        return sm

if __name__ == '__main__':
    POSitApp().run()
        