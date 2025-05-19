from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from adminNav import NavBar
from models import User, Admin
import auth
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
import re # Import regular expressions

# Placeholder for accent color, adapt as needed
ACCENT_BLUE = (0.22, 0.27, 0.74, 1)
LIGHT_GRAY_BG = (0.95, 0.95, 0.95, 1)
WHITE = (1, 1, 1, 1)

def get_users():
    """Returns a list of all users."""
    return auth.get_users()

def add_user(user_data):
    """Adds a new user. user_data should include 'username', 'password', 'role'."""
    # Create a new User or Admin object based on role
    role = user_data['role'].lower()
    if role == 'admin':
        new_user = Admin(user_data['username'], user_data['password'])  # Admin class automatically sets role to "admin"
    else:
        new_user = User(user_data['username'], user_data['password'], role)  # User class needs role specified
    
    auth._users_list.append(new_user)
    print(f"User added: {new_user.username} ({new_user.role})")

def update_user(user_id, update_data):
    """Updates an existing user."""
    for user in auth._users_list:
        if user.username == user_id:  # Using username as ID
            if 'username' in update_data:
                user.username = update_data['username']
            if 'password' in update_data and update_data['password']:
                user.hashPass = update_data['password']  # In real app, hash this
            print(f"User updated: {user.username} ({user.role})")
            return True
    return False

def remove_user(user_id):
    """Removes a user by username."""
    auth._users_list[:] = [user for user in auth._users_list if user.username != user_id]
    print(f"User removed: {user_id}")

class UserEditPopup(Popup):
    def __init__(self, user=None, on_save=None, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Edit User' if user else 'Add New User'
        self.size_hint = (0.5, 0.7)
        self.user = user
        self.on_save = on_save
        
        self.original_password_hint = 'New Password (leave blank to keep current)' if user else 'Password'
        self.original_username_hint = 'Username'
        # It seems Kivy's default hint_text_color is (0,0,0,0.5) but let's be explicit
        # or use a theme-consistent color if you have one.
        self.default_hint_text_color = (0,0,0,0.5) # Standard Kivy hint text color

        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        self.username_input = TextInput(
            text=user.username if user else '',
            hint_text=self.original_username_hint,
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            hint_text_color=self.default_hint_text_color
        )
        
        # For password, only prompt for new password. If blank on edit, don't change.
        # password_hint = 'New Password (leave blank to keep current)' if user else 'Password' # Now uses self.original_password_hint
        self.password_input = TextInput(
            hint_text=self.original_password_hint,
            multiline=False,
            password=True,
            size_hint_y=None,
            height=dp(40),
            hint_text_color=self.default_hint_text_color
        )
        
        self.role_spinner = Spinner(
            text='Admin' if user and user.role == 'admin' else 'Cashier',
            values=('Admin', 'Cashier'),
            size_hint_y=None,
            height=dp(44)
        )

        layout.add_widget(Label(text='Username', size_hint_y=None, height=dp(20)))
        layout.add_widget(self.username_input)
        layout.add_widget(Label(text='Password', size_hint_y=None, height=dp(20)))
        layout.add_widget(self.password_input)
        layout.add_widget(Label(text='Role', size_hint_y=None, height=dp(20)))
        layout.add_widget(self.role_spinner)

        layout.add_widget(BoxLayout(size_hint_y=1))  # Spacer

        btn_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        save_btn = Button(text='Save', on_release=self.save_user)
        cancel_btn = Button(text='Cancel', on_release=self.dismiss)
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        layout.add_widget(btn_layout)

        self.content = layout

    def _is_password_valid(self, password):
        """Checks if the password meets the defined criteria."""
        
        # Tier 1: Length
        if len(password) < 8:
            return False, "Password must be at least 8 characters long."

        # Tier 2: Case
        case_errors = []
        if not re.search(r"[A-Z]", password):
            case_errors.append("an uppercase letter")
        if not re.search(r"[a-z]", password):
            case_errors.append("a lowercase letter")
        if case_errors:
            return False, "Password must contain " + " and ".join(case_errors) + "."

        # Tier 3: Numbers and Symbols
        char_type_errors = []
        if not re.search(r"[0-9]", password):
            char_type_errors.append("a number")
        if not re.search(r"[\W_]", password): # \W is non-alphanumeric (includes underscore)
            char_type_errors.append("a symbol (e.g., !@#$%)")
        if char_type_errors:
            return False, "Password must contain " + " and ".join(char_type_errors) + "."
        
        # If all tiers pass
        return True, ""

    def save_user(self, instance):
        # Basic validation
        username = self.username_input.text.strip()
        password_text = self.password_input.text # Don't strip, spaces might be intentional
        role = 'admin' if self.role_spinner.text == 'Admin' else 'user'

        if not username:
            self.username_input.hint_text = "Username cannot be empty."
            self.username_input.hint_text_color = (1, 0, 0, 1) # Red
            # Optionally clear the input or leave it as is
            # self.username_input.text = "" 
            return

        # Password validation logic
        if self.user: # Editing existing user
            if password_text: # Password field is not empty, so user wants to change it
                is_valid, error_message = self._is_password_valid(password_text)
                if not is_valid:
                    self.password_input.hint_text = error_message
                    self.password_input.hint_text_color = (1, 0, 0, 1) # Red
                    self.password_input.text = "" # Clear the invalid password
                    return
            # else: password field is empty, so don't change password, no validation needed
        else: # Adding new user
            if not password_text:
                self.password_input.hint_text = "Password is required for new user."
                self.password_input.hint_text_color = (1, 0, 0, 1) # Red
                return
            is_valid, error_message = self._is_password_valid(password_text)
            if not is_valid:
                self.password_input.hint_text = error_message
                self.password_input.hint_text_color = (1, 0, 0, 1) # Red
                self.password_input.text = "" # Clear the invalid password
                return

        # If validation passed or password not being changed, reset hint text style
        self.password_input.hint_text = self.original_password_hint
        self.password_input.hint_text_color = self.default_hint_text_color
        
        # Reset username hint text style if it passed validation
        self.username_input.hint_text = self.original_username_hint
        self.password_input.hint_text_color = self.default_hint_text_color

        # Prepare data for saving
        final_data = {
            'username': username,
            'role': role,
        }
        if password_text: # Only include password if it was provided (and validated)
            final_data['password'] = password_text

        if self.on_save:
            self.on_save(final_data, is_new_user=(not self.user))
        self.dismiss()

class IconButton(ButtonBehavior, Image):
    pass

class UserManagementScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set background color to LIGHT_GRAY_BG at the Screen level
        with self.canvas.before:
            Color(*LIGHT_GRAY_BG)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(NavBar())

        content_area = BoxLayout(orientation='vertical', padding=[dp(32), dp(32), dp(32), dp(32)], spacing=dp(24), size_hint=(1, 1))

        title_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(60))
        title = Label(text='User Management', font_size=dp(20), bold=True, color=(0,0,0,1), halign='left', valign='bottom', size_hint_y=None, height=dp(30))
        title.bind(texture_size=title.setter('size'))
        title_layout.add_widget(title)
        subtitle = Label(text='Add, modify, and manage user accounts and permissions', font_size=dp(14), color=(0,0,0,0.6), halign='left', valign='top', size_hint_y=None, height=dp(30))
        subtitle.bind(texture_size=subtitle.setter('size'))
        title_layout.add_widget(subtitle)
        content_area.add_widget(title_layout)

        action_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        self.search_input = TextInput(
            hint_text='Search users (by username or role)...',
            multiline=False,
            size_hint_x=0.7,
            background_color=(0,0,0,0),
            background_normal='',
            foreground_color=(0,0,0,1),
            cursor_color=ACCENT_BLUE,
            padding=[dp(5), dp(10), dp(5), dp(10)]
        )
        # Add a bottom border using canvas.after
        with self.search_input.canvas.after:
            Color(0, 0, 0, 1)
            self._search_border_line = Line(points=[], width=1.2)
        def update_search_border(instance, value):
            x, y = instance.x, instance.y
            w = instance.width
            self._search_border_line.points = [x, y, x + w, y]
        self.search_input.bind(pos=update_search_border, size=update_search_border)
        self.search_input.bind(text=lambda instance, value: self.refresh_user_table())
        action_bar.add_widget(self.search_input)

        add_user_btn = Button(
            text='+ Add New User',
            size_hint_x=0.3,
            background_color=ACCENT_BLUE,
            background_normal='',
            color=(1,1,1,1)
        )
        def on_add_btn_press(instance):
            instance.background_color = (0.16, 0.20, 0.55, 1)
        def on_add_btn_release(instance):
            instance.background_color = ACCENT_BLUE
        add_user_btn.bind(on_press=on_add_btn_press, on_release=on_add_btn_release)
        add_user_btn.bind(on_release=self.open_add_user_popup)
        action_bar.add_widget(add_user_btn)
        content_area.add_widget(action_bar)

        # Table in a white rounded rectangle card
        table_card = BoxLayout(orientation='vertical', size_hint=(1, 1), padding=[dp(16), dp(16), dp(16), dp(16)], spacing=dp(0))
        with table_card.canvas.before:
            Color(*WHITE)
            table_card.bg_rect = RoundedRectangle(size=table_card.size, pos=table_card.pos, radius=[(dp(16), dp(16))] * 4)
        table_card.bind(size=lambda instance, value: setattr(instance.bg_rect, 'size', instance.size))
        table_card.bind(pos=lambda instance, value: setattr(instance.bg_rect, 'pos', instance.pos))

        # Table Header
        header = GridLayout(cols=3, size_hint_y=None, height=dp(40), spacing=dp(1))
        header.size_hint_x = 1
        header_col_hints = [1.2, 1, 0.6]
        header_cols = ['Username', 'Role', 'Actions']
        for i, col_text in enumerate(header_cols):
            header.add_widget(Label(text=col_text, bold=True, color=(0,0,0,0.8), size_hint_x=header_col_hints[i]))
        table_card.add_widget(header)

        # User Table (Scrollable)
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.user_table = GridLayout(cols=3, size_hint_y=None, spacing=dp(1), row_default_height=dp(40), row_force_default=True)
        self.user_table.size_hint_x = 1
        self.user_col_hints = [1.2, 1, 0.6]
        self.user_table.bind(minimum_height=self.user_table.setter('height'))
        self.scroll_view.add_widget(self.user_table)
        table_card.add_widget(self.scroll_view)
        content_area.add_widget(table_card)

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
        users = get_users()

        for idx, user in enumerate(users):
            if search_term and not (search_term in user.username.lower() or \
                                   search_term in user.role.lower()):
                continue

            # Row with alternating background (white and light blue)
            row_bg_color = (1, 1, 1, 1) if idx % 2 == 0 else (0.22, 0.27, 0.74, 0.08)

            # Username
            uname_label = Label(text=user.username, color=(0,0,0,1), size_hint_x=self.user_col_hints[0])
            with uname_label.canvas.before:
                Color(*row_bg_color)
                Rectangle(size=uname_label.size, pos=uname_label.pos)
            uname_label.row_bg_color = row_bg_color
            uname_label.bind(size=self._update_cell_bg, pos=self._update_cell_bg)
            self.user_table.add_widget(uname_label)

            # Role
            display_role = 'Admin' if user.role == 'admin' else 'Cashier'
            role_label = Label(text=display_role, color=(0,0,0,1), size_hint_x=self.user_col_hints[1])
            with role_label.canvas.before:
                Color(*row_bg_color)
                Rectangle(size=role_label.size, pos=role_label.pos)
            role_label.row_bg_color = row_bg_color
            role_label.bind(size=self._update_cell_bg, pos=self._update_cell_bg)
            self.user_table.add_widget(role_label)

            # Actions
            actions_layout = BoxLayout(orientation='horizontal', spacing=dp(6), padding=(0,0,0,0), size_hint_x=self.user_col_hints[2], size_hint_y=1)
            with actions_layout.canvas.before:
                Color(*row_bg_color)
                Rectangle(size=actions_layout.size, pos=actions_layout.pos)
            actions_layout.row_bg_color = row_bg_color
            actions_layout.bind(size=self._update_cell_bg, pos=self._update_cell_bg)

            # Add left spacer
            actions_layout.add_widget(Widget())
            # Edit button (icon)
            edit_btn = IconButton(source='icons/edit.png', size_hint=(None, None), width=dp(24), height=dp(24))
            edit_btn.bind(on_release=lambda instance, u=user: self.open_edit_user_popup(u))
            actions_layout.add_widget(edit_btn)

            # Delete button (icon)
            delete_btn = IconButton(source='icons/delete.png', size_hint=(None, None), width=dp(24), height=dp(24))
            delete_btn.bind(on_release=lambda instance, u=user: self.confirm_delete_user(u.username))
            actions_layout.add_widget(delete_btn)
            # Add right spacer
            actions_layout.add_widget(Widget())

            self.user_table.add_widget(actions_layout)

    def open_add_user_popup(self, instance):
        def save_callback(data, is_new_user):
            add_user(data)
            self.refresh_user_table()

        popup = UserEditPopup(user=None, on_save=save_callback)
        popup.open()

    def open_edit_user_popup(self, user):
        def save_callback(data, is_new_user):
            update_user(user.username, data)
            self.refresh_user_table()

        popup = UserEditPopup(user=user, on_save=save_callback)
        popup.open()

    def confirm_delete_user(self, username):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        content.add_widget(Label(text=f"Are you sure you want to delete user {username}?\nThis action cannot be undone.", halign='center'))
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        confirm_btn = Button(text='Delete', background_color=(0.9,0.2,0.2,1))
        cancel_btn = Button(text='Cancel')
        btn_layout.add_widget(confirm_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup = Popup(title='Confirm Deletion', content=content, size_hint=(0.4, 0.3))
        
        def do_delete(*args):
            remove_user(username)
            self.refresh_user_table()
            popup.dismiss()

        confirm_btn.bind(on_release=do_delete)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    from kivy.app import App
    class TestApp(App):
        def build(self):
            return UserManagementScreen(name='user_management')
    TestApp().run()