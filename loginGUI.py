'''from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

import auth
from models import User, Admin

# This is the login screen (extends Screen)
class LoginScreen(Screen):
    def __init__(self, users, **kwargs):
        super().__init__(**kwargs)
        self.users = users  # store users locally

        layout = BoxLayout(orientation='vertical')

        self.label = Label(text="Login", font_size=24)
        layout.add_widget(self.label)

        self.username = TextInput(hint_text='Username', multiline=False)
        layout.add_widget(self.username)

        self.password = TextInput(hint_text='Password', multiline=False, password=True)
        layout.add_widget(self.password)

        self.login_btn = Button(text="Login")
        self.login_btn.bind(on_press=self.login)
        layout.add_widget(self.login_btn)

        self.message = Label(text="")
        layout.add_widget(self.message)

        self.add_widget(layout)


    def login(self, instance):
        uname = self.username.text
        pword = self.password.text
        role = auth.authUser(self.users, uname, pword)  # use self.users

        if role:
            auth.setUserSession(uname, role)
            self.message.text = f"Welcome {uname} ({role})"
            self.manager.current = "home"
        else:
            self.message.text = "Invalid credentials"'''
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

import auth
from models import User, Admin


class LoginScreen(Screen):
    def __init__(self, users, **kwargs):
        super().__init__(**kwargs)
        from kivy.core.window import Window
        Window.bind(on_key_down=self._on_key_down)
        
        
        self.users = users  # store users locally
        
        # Custom TextInput focus behavior
        self.focused_input = None
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Create a styled form layout
        form_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint=(1, 0.8))
        
        # Username section
        username_label = Label(text="Username", halign='left', size_hint=(1, None), height=dp(30),
                              color=(0, 0, 0, 1), font_size=dp(14))
        username_label.bind(size=self._update_label)
        self.username = TextInput(
            hint_text='Enter your username',
            multiline=False,
            size_hint=(1, None),
            height=dp(40),
            padding=[dp(10), dp(10)],
            background_color=(1, 1, 1, 0),
            foreground_color=(0, 0, 0, 1),
            border=(0, 0, 0, 0),  # Remove default border
            cursor_color=(0.3, 0.5, 0.9, 1)  # Blue cursor
        )
        
        # Password section
        password_label = Label(text="Password", halign='left', size_hint=(1, None), height=dp(30),
                              color=(0, 0, 0, 1), font_size=dp(14))
        password_label.bind(size=self._update_label)
        self.password = TextInput(
            hint_text='Enter your password',
            multiline=False,
            password=True,
            size_hint=(1, None),
            height=dp(40),
            padding=[dp(10), dp(10)],
            background_color=(1, 1, 1, 0),
            foreground_color=(0, 0, 0, 1),
            border=(0, 0, 0, 0),  # Remove default border
            cursor_color=(0.3, 0.5, 0.9, 1)  # Blue cursor
        )
        
        # Remember me checkbox
        remember_layout = BoxLayout(size_hint=(1, None), height=dp(30))
        self.remember_checkbox = CheckBox(size_hint=(None, None), size=(dp(30), dp(30)))
        remember_label = Label(
            text="Remember me",
            color=(0, 0, 0, 0.8),
            font_size=dp(14),
            halign='left'
        )
        remember_label.bind(size=self._update_label)
        remember_layout.add_widget(self.remember_checkbox)
        remember_layout.add_widget(remember_label)
        
        # Forgot password link
        forgot_password = BoxLayout(size_hint=(1, None), height=dp(30))
        forgot_password_spacer = Label(size_hint=(1, None), height=dp(30))
        forgot_password_label = Label(
            text="Forgot password?",
            color=(0.3, 0.5, 0.9, 1),
            size_hint=(1, None),
            height=dp(30),
            halign='right',
            font_size=dp(14)
        )
        forgot_password_label.bind(size=self._update_label)
        forgot_password.add_widget(forgot_password_spacer)
        forgot_password.add_widget(forgot_password_label)
        normal_color = (0.22, 0.27, 0.74, 1)  # #3944BC in RGBA
        pressed_color = (0.18, 0.22, 0.64, 1)  # Slightly darker shade for pressed state    
        # Login button
        self.login_btn = Button(
            text="Login",
            size_hint=(1, None),
            height=dp(50),
            background_normal='',  # Set an empty string to not use an image
            background_color=normal_color,  # Sky blue color by default
            background_disabled_normal='',  # Disable background image on disabled state
            background_disabled_down='',  # Disable background image when disabled
            color=(1, 1, 1, 1),  # Text color
            font_size=dp(16)
    )
        self.focusables = [
        self.username,
        self.password,
        self.remember_checkbox,
        self.login_btn
        ]
        
        for widget in self.focusables:
            if hasattr(widget, 'focus'):
                widget.bind(focus=self.on_focus)

    # Bind the button's on_press and on_release to change the color dynamically
        def on_press(instance):
            instance.background_color = pressed_color
        def on_release(instance):
            instance.background_color = normal_color
        
        self.login_btn.bind(on_press=on_press)
        self.login_btn.bind(on_release=self.login)
        self.login_btn.bind(on_press=on_press)
        self.login_btn.bind(on_release=on_release)
        
        # Error message
        self.message = Label(
            text="",
            color=(0.9, 0.3, 0.3, 1),
            size_hint=(1, None),
            height=dp(30)
        )
        
        # Add all widgets to form layout
        form_layout.add_widget(username_label)
        form_layout.add_widget(self.username)
        form_layout.add_widget(password_label)
        form_layout.add_widget(self.password)
        
        # Extra elements layout
        extras_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(30))
        extras_layout.add_widget(remember_layout)
        extras_layout.add_widget(forgot_password)
        
        form_layout.add_widget(extras_layout)
        form_layout.add_widget(self.login_btn)
        form_layout.add_widget(self.message)
        
        # Add form to main layout
        main_layout.add_widget(form_layout)
        
        # Add spacers at the top and bottom
        main_layout.add_widget(BoxLayout(size_hint=(1, 0.2)))  # Bottom spacer
        
        # Add everything to the screen
        self.add_widget(main_layout)
        
        # Add a white background
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        # Initial border for text inputs (gray)
        with self.username.canvas.after:
            Color(0.8, 0.8, 0.8, 1)  # Gray border
            Rectangle(pos=[self.username.x, self.username.y], size=[self.username.width, dp(1)])
            
        with self.password.canvas.after:
            Color(0.8, 0.8, 0.8, 1)  # Gray border
            Rectangle(pos=[self.password.x, self.password.y], size=[self.password.width, dp(1)])
            
        # Bind size and position updates for the borders
        self.username.bind(size=self._update_input_border, pos=self._update_input_border)
        self.password.bind(size=self._update_input_border, pos=self._update_input_border)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos
        
    def _update_label(self, instance, value):
        instance.text_size = (instance.width, None)
    
    def _update_input_border(self, instance, value):
        instance.canvas.after.clear()
        if self.focused_input == instance:
            with instance.canvas.after:
                Color(0.3, 0.5, 0.9, 1)  # Blue border
                Rectangle(pos=[instance.x, instance.y], size=[instance.width, dp(2)])
        else:
            with instance.canvas.after:
                Color(0.8, 0.8, 0.8, 1)  # Gray border
                Rectangle(pos=[instance.x, instance.y], size=[instance.width, dp(1)])
                
    def _on_dropdown_select(self, instance, value):
        self.dropdown_btn.text = value
        self.access_level = value
        
    def on_focus(self, instance, value):
        # When focused, add blue border
        if value:  # If focused
            self.focused_input = instance
            instance.canvas.after.clear()
            with instance.canvas.after:
                Color(0.3, 0.5, 0.9, 1)  # Blue border
                Rectangle(pos=[instance.x, instance.y], size=[instance.width, dp(2)])
        else:  # If not focused
            instance.canvas.after.clear()
            with instance.canvas.after:
                Color(0.8, 0.8, 0.8, 1)  # Gray border
                Rectangle(pos=[instance.x, instance.y], size=[instance.width, dp(1)])
    
    def login(self, instance):
        uname = self.username.text
        pword = self.password.text

    # Check if password is not empty
        if not pword:
            self.message.text = "Please enter your password."
            return

        try:
        # Use both username and password for authentication
            role = auth.authUser(self.users, uname, pword)  # Pass username and password
            if role:
                auth.setUserSession(uname, role)
                self.message.text = f"Welcome {uname} ({role})"
                self.manager.current = "home"
            else:
                self.message.text = "Invalid credentials"
        except Exception as e:
            print(f"Error during login: {e}")
            self.message.text = "An error occurred. Please try again."
            
        
        
    def _on_key_down(self, window, key, scancode, codepoint, modifier):
        if key == 9:  # Tab key
            current = self.focused_input or None
            if current in self.focusables:
                idx = self.focusables.index(current)
                next_idx = (idx + 1) % len(self.focusables)
            else:
                next_idx = 0
            next_widget = self.focusables[next_idx]

            if hasattr(next_widget, 'focus'):
                next_widget.focus = True
                self.focused_input = next_widget
            return True  # Stop further handling
        
    