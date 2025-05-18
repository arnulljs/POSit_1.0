from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner # For role selection
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, Line
from adminNav import NavBar # Assuming NavBar is in adminNav.py

# Placeholder for accent color, adapt as needed
ACCENT_BLUE = (0.22, 0.27, 0.74, 1)

# --- Placeholder User Data Management ---
# In a real app, these would interact with auth.py or a database

_users_db = [
    {'user_id': 'USR001', 'username': 'admin_user', 'role': 'admin', 'password_hash': 'hashed_password_admin'},
    {'user_id': 'USR002', 'username': 'standard_user1', 'role': 'user', 'password_hash': 'hashed_password_user1'},
    {'user_id': 'USR003', 'username': 'another_user', 'role': 'user', 'password_hash': 'hashed_password_user2'},
]
_next_user_id_counter = 4

def get_users_mock():
    """Returns a list of all users."""
    return list(_users_db)

def get_next_user_id_mock():
    """Generates a new user ID."""
    global _next_user_id_counter
    new_id = f"USR{_next_user_id_counter:03d}"
    _next_user_id_counter += 1
    return new_id

def add_user_mock(user_data):
    """Adds a new user. user_data should include 'username', 'password', 'role'."""
    # In a real app, hash the password before storing
    new_user = {
        'user_id': user_data.get('user_id', get_next_user_id_mock()),
        'username': user_data['username'],
        # Map 'Admin' to 'admin' and 'Cashier' to 'user'
        'role': 'admin' if user_data['role'].lower() == 'admin' else 'user',
        'password_hash': f"hashed_{user_data['password']}" # Placeholder for hashing
    }
    _users_db.append(new_user)
    print(f"User added: {new_user}")

def update_user_mock(user_id, update_data):
    """Updates an existing user. update_data can include 'username', 'password', 'role'."""
    for user in _users_db:
        if user['user_id'] == user_id:
            if 'username' in update_data:
                user['username'] = update_data['username']
            if 'role' in update_data:
                # Map 'Admin' to 'admin' and 'Cashier' to 'user'
                user['role'] = 'admin' if update_data['role'].lower() == 'admin' else 'user'
            if 'password' in update_data and update_data['password']: # Only update password if provided
                user['password_hash'] = f"hashed_{update_data['password']}" # Placeholder
            print(f"User updated: {user}")
            return True
    return False

def remove_user_mock(user_id):
    """Removes a user by user_id."""
    global _users_db
    _users_db = [user for user in _users_db if user['user_id'] != user_id]
    print(f"User removed: {user_id}")

# --- End Placeholder User Data Management ---

class UserEditPopup(Popup):
    def __init__(self, user=None, on_save=None, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Edit User' if user else 'Add New User'
        self.size_hint = (0.5, 0.7)
        self.user = user or {}
        self.on_save = on_save

        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        self.user_id_input = TextInput(
            text=self.user.get('user_id', get_next_user_id_mock()),
            hint_text='User ID', multiline=False, readonly=True,
            size_hint_y=None, height=dp(40)
        )
        self.username_input = TextInput(
            text=self.user.get('username', ''), hint_text='Username',
            multiline=False, size_hint_y=None, height=dp(40)
        )
        # For password, only prompt for new password. If blank on edit, don't change.
        password_hint = 'New Password (leave blank to keep current)' if user else 'Password'
        self.password_input = TextInput(
            hint_text=password_hint, multiline=False, password=True,
            size_hint_y=None, height=dp(40)
        )
        self.role_spinner = Spinner(
            # Display 'Admin' for 'admin' role, 'Cashier' for 'user' role. Default to 'Cashier'.
            text='Admin' if self.user.get('role', 'user') == 'admin' else 'Cashier',
            values=('Admin', 'Cashier'), # Roles available in UI
            size_hint_y=None, height=dp(44) # Spinners need a bit more height
        )

        layout.add_widget(Label(text='User ID', size_hint_y=None, height=dp(20)))
        layout.add_widget(self.user_id_input)
        layout.add_widget(Label(text='Username', size_hint_y=None, height=dp(20)))
        layout.add_widget(self.username_input)
        layout.add_widget(Label(text='Password', size_hint_y=None, height=dp(20)))
        layout.add_widget(self.password_input)
        layout.add_widget(Label(text='Role', size_hint_y=None, height=dp(20)))
        layout.add_widget(self.role_spinner)

        layout.add_widget(BoxLayout(size_hint_y=1)) # Spacer

        btn_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        save_btn = Button(text='Save', on_release=self.save_user)
        cancel_btn = Button(text='Cancel', on_release=self.dismiss)
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        layout.add_widget(btn_layout)

        self.content = layout

    def save_user(self, instance):
        # Basic validation
        if not self.username_input.text.strip():
            # Simple error feedback, could be a small popup too
            print("Error: Username cannot be empty.")
            return
        if not self.user and not self.password_input.text: # Password required for new user
             print("Error: Password cannot be empty for new user.")
             return

        data = {
            'user_id': self.user_id_input.text.strip(),
            'username': self.username_input.text.strip(),
            # Convert UI role ('Admin'/'Cashier') to internal role ('admin'/'user')
            'role': 'admin' if self.role_spinner.text == 'Admin' else 'user',
            # Only include password if it's a new user or if text is entered for an existing one
            'password': self.password_input.text if self.password_input.text or not self.user else None
        }
        # Filter out None password if not provided for update
        if data['password'] is None:
            del data['password']

        if self.on_save:
            self.on_save(data, is_new_user=(not self.user))
        self.dismiss()

class UserManagementScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)  # White background
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(NavBar()) # Add NavBar

        content_area = BoxLayout(orientation='vertical', padding=[dp(20), dp(10)], spacing=dp(15))

        title_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(60))
        title = Label(text='User Management', font_size=dp(20), bold=True, color=(0,0,0,1), halign='left', valign='bottom', size_hint_y=None, height=dp(30))
        title.bind(texture_size=title.setter('size')) # Ensure text fits
        title_layout.add_widget(title)
        subtitle = Label(text='Add, modify, and manage user accounts and permissions', font_size=dp(14), color=(0,0,0,0.6), halign='left', valign='top', size_hint_y=None, height=dp(30))
        subtitle.bind(texture_size=subtitle.setter('size'))
        title_layout.add_widget(subtitle)
        content_area.add_widget(title_layout)

        action_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        self.search_input = TextInput(hint_text='Search users (by username or role)...', multiline=False, size_hint_x=0.7)
        self.search_input.bind(text=lambda instance, value: self.refresh_user_table())
        action_bar.add_widget(self.search_input)

        add_user_btn = Button(text='+ Add New User', size_hint_x=0.3, background_color=ACCENT_BLUE, color=(1,1,1,1))
        add_user_btn.bind(on_release=self.open_add_user_popup)
        action_bar.add_widget(add_user_btn)
        content_area.add_widget(action_bar)

        # Table Header
        header = GridLayout(cols=4, size_hint_y=None, height=dp(40), spacing=dp(1))
        header_cols = ['User ID', 'Username', 'Role', 'Actions']
        for col_text in header_cols:
            header.add_widget(Label(text=col_text, bold=True, color=(0,0,0,0.8)))
        content_area.add_widget(header)

        # User Table (Scrollable)
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.user_table = GridLayout(cols=4, size_hint_y=None, spacing=dp(1), row_default_height=dp(40), row_force_default=True)
        self.user_table.bind(minimum_height=self.user_table.setter('height'))
        self.scroll_view.add_widget(self.user_table)
        content_area.add_widget(self.scroll_view)

        self.layout.add_widget(content_area)
        self.add_widget(self.layout)
        self.refresh_user_table()

    def _update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def _update_cell_bg(self, instance, *args):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*instance.row_bg_color)
            Rectangle(pos=instance.pos, size=instance.size)

    def refresh_user_table(self):
        self.user_table.clear_widgets()
        search_term = self.search_input.text.strip().lower()
        users = get_users_mock()

        for idx, user_data in enumerate(users):
            if search_term and not (search_term in user_data['username'].lower() or \
                                   search_term in user_data['user_id'].lower() or \
                                   search_term in user_data['role'].lower()):
                continue

            row_bg_color = (0.95, 0.95, 0.95, 1) if idx % 2 == 0 else (1, 1, 1, 1)

            # User ID
            uid_label = Label(text=user_data['user_id'], color=(0,0,0,1))
            uid_label.row_bg_color = row_bg_color
            uid_label.bind(size=self._update_cell_bg, pos=self._update_cell_bg)
            self.user_table.add_widget(uid_label)

            # Username
            uname_label = Label(text=user_data['username'], color=(0,0,0,1))
            uname_label.row_bg_color = row_bg_color
            uname_label.bind(size=self._update_cell_bg, pos=self._update_cell_bg)
            self.user_table.add_widget(uname_label)

            # Role
            # Display 'Admin' for 'admin' role, 'Cashier' for 'user' role
            display_role = 'Admin' if user_data['role'] == 'admin' else 'Cashier'
            role_label = Label(text=display_role, color=(0,0,0,1))
            role_label.row_bg_color = row_bg_color
            role_label.bind(size=self._update_cell_bg, pos=self._update_cell_bg)
            self.user_table.add_widget(role_label)

            # Actions
            actions_layout = BoxLayout(orientation='horizontal', spacing=dp(5), padding=(dp(5),0))
            actions_layout.row_bg_color = row_bg_color # Important for background
            actions_layout.bind(size=self._update_cell_bg, pos=self._update_cell_bg)

            edit_btn = Button(text='Edit', size_hint_x=None, width=dp(70))
            edit_btn.bind(on_release=lambda instance, u=user_data: self.open_edit_user_popup(u))
            actions_layout.add_widget(edit_btn)

            delete_btn = Button(text='Delete', size_hint_x=None, width=dp(70), background_color=(0.9,0.2,0.2,1)) # Reddish
            delete_btn.bind(on_release=lambda instance, u_id=user_data['user_id']: self.confirm_delete_user(u_id))
            actions_layout.add_widget(delete_btn)
            
            self.user_table.add_widget(actions_layout)

    def open_add_user_popup(self, instance):
        def save_callback(data, is_new_user):
            add_user_mock(data)
            self.refresh_user_table()

        popup = UserEditPopup(user=None, on_save=save_callback)
        popup.open()

    def open_edit_user_popup(self, user_data):
        def save_callback(data, is_new_user):
            update_user_mock(user_data['user_id'], data)
            self.refresh_user_table()

        popup = UserEditPopup(user=user_data, on_save=save_callback)
        popup.open()

    def confirm_delete_user(self, user_id):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        content.add_widget(Label(text=f"Are you sure you want to delete user {user_id}?\nThis action cannot be undone.", halign='center'))
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        confirm_btn = Button(text='Delete', background_color=(0.9,0.2,0.2,1))
        cancel_btn = Button(text='Cancel')
        btn_layout.add_widget(confirm_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup = Popup(title='Confirm Deletion', content=content, size_hint=(0.4, 0.3))
        
        def do_delete(*args):
            remove_user_mock(user_id)
            self.refresh_user_table()
            popup.dismiss()

        confirm_btn.bind(on_release=do_delete)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

if __name__ == '__main__': # For testing this screen directly
    from kivy.app import App
    class TestApp(App):
        def build(self):
            return UserManagementScreen(name='user_management')
    TestApp().run()