from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.core.window import Window

import auth
from models import User, Admin

ACCENT_BLUE = (0.22, 0.27, 0.74, 1)

class LoginScreen(Screen):
    def __init__(self, users, **kwargs):
        super().__init__(**kwargs)
        self.users = users

        # Root layout: horizontal BoxLayout fills the window
        root_layout = BoxLayout(orientation='horizontal')

        # Left panel (blue)
        left_panel = BoxLayout(orientation='vertical', size_hint_x=0.45, padding=[dp(32), dp(32), dp(32), dp(32)], spacing=dp(20))
        with left_panel.canvas.before:
            Color(*ACCENT_BLUE)
            self.left_rect = Rectangle(size=left_panel.size, pos=left_panel.pos)
        left_panel.bind(size=self._update_left_bg, pos=self._update_left_bg)
        
        # Left side content
        left_content = BoxLayout(orientation='vertical', padding=[dp(40), dp(40), dp(40), dp(40)])
        
        # Title with larger font and proper spacing
        title = Label(
            text='POSit',
            font_size=dp(48),
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(60),
            halign='center',
            valign='middle'
        )
        title.bind(size=self._update_text_size)
        
        # Description with proper spacing and alignment
        description = Label(
            text='Your all-in-one point of sale solution for seamless transactions and efficient business management.',
            font_size=dp(16),
            color=(1, 1, 1, 0.9),
            size_hint=(1, None),
            height=dp(80),
            halign='center',
            valign='middle',
            text_size=(None, None)
        )
        description.bind(size=self._update_text_size)
        
        # Add widgets to left content with proper spacing
        left_content.add_widget(Widget(size_hint_y=0.3))  # Top spacer
        left_content.add_widget(title)
        left_content.add_widget(description)
        left_content.add_widget(Widget(size_hint_y=0.7))  # Bottom spacer

        # Add left_content to left_panel
        left_panel.add_widget(left_content)
        root_layout.add_widget(left_panel)

        # Right panel (white, fills remaining space)
        right_panel = BoxLayout(orientation='vertical', padding=[dp(40), dp(32), dp(40), dp(32)], spacing=dp(10), size_hint_x=0.55)
        with right_panel.canvas.before:
            Color(1, 1, 1, 1)
            self.right_rect = Rectangle(size=right_panel.size, pos=right_panel.pos)
        right_panel.bind(size=self._update_right_bg, pos=self._update_right_bg)

        # Add vertical spacers to center the form
        right_panel.add_widget(Widget(size_hint_y=1))  # Top spacer

        form_box = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        form_box.bind(minimum_height=form_box.setter('height'))

        # Welcome and instructions
        welcome = Label(text="[b]Welcome Back[/b]", markup=True, font_size=dp(24), color=(0,0,0,1), size_hint=(1, None), height=dp(40))
        form_box.add_widget(welcome)
        instructions = Label(text="Please log in with your company credentials", color=(0.3,0.3,0.3,1), font_size=dp(14), size_hint=(1, None), height=dp(24))
        form_box.add_widget(instructions)
        form_box.add_widget(Label(text="", size_hint=(1, None), height=dp(10)))

        # Username
        username_label = Label(text="Username", color=(0,0,0,1), font_size=dp(14), size_hint=(1, None), height=dp(24), halign='left', valign='middle')
        username_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
        form_box.add_widget(username_label)
        self.username = TextInput(hint_text='Enter your username', multiline=False, size_hint=(1, None), height=dp(40), font_size=dp(16), padding=[dp(10), dp(10)], background_color=(0,0,0,0), foreground_color=(0,0,0,1), cursor_color=(0.22,0.27,0.74,1), background_normal='', background_active='')
        form_box.add_widget(self.username)
        with self.username.canvas.after:
            Color(0, 0, 0, 1)
            self.username_border = Rectangle(pos=(self.username.x, self.username.y), size=(self.username.width, 1))
        self.username.bind(pos=self._update_username_border, size=self._update_username_border)

        # Password
        password_label = Label(text="Password", color=(0,0,0,1), font_size=dp(14), size_hint=(1, None), height=dp(24), halign='left', valign='middle')
        password_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
        form_box.add_widget(password_label)
        self.password = TextInput(hint_text='Enter your password', multiline=False, password=True, size_hint=(1, None), height=dp(40), font_size=dp(16), padding=[dp(10), dp(10)], background_color=(0,0,0,0), foreground_color=(0,0,0,1), cursor_color=(0.22,0.27,0.74,1), background_normal='', background_active='')
        form_box.add_widget(self.password)
        with self.password.canvas.after:
            Color(0, 0, 0, 1)
            self.password_border = Rectangle(pos=(self.password.x, self.password.y), size=(self.password.width, 1))
        self.password.bind(pos=self._update_password_border, size=self._update_password_border)

        # Add a spacer to separate password and remember me
        form_box.add_widget(Label(text="", size_hint=(1, None), height=dp(10)))

        # Remember me and forgot password
        extras_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(24), spacing=dp(0))
        self.remember_checkbox = CheckBox(size_hint=(None, None), size=(dp(24), dp(24)))
        remember_label = Label(
            text="Remember me",
            color=(0,0,0,1),
            font_size=dp(14),
            size_hint=(None, None),
            height=dp(24),
            halign='left',
            valign='middle'
        )
        remember_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, inst.height)))
        extras_layout.add_widget(self.remember_checkbox)
        extras_layout.add_widget(remember_label)
        form_box.add_widget(extras_layout)

        # Login button
        self.login_btn = Button(
            text="Login",
            size_hint=(1, None),
            height=dp(50),
            background_normal='',
            background_color=ACCENT_BLUE,
            color=(1, 1, 1, 1),
            font_size=dp(16)
        )
        self.login_btn.bind(on_release=self.login)
        form_box.add_widget(self.login_btn)

        # Skip login buttons
        skip_btns_box = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(40), spacing=dp(10))
        skip_admin_btn = Button(
            text="Skip as Admin",
            size_hint=(0.5, 1),
            background_normal='',
            background_color=(0.2, 0.7, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size=dp(14)
        )
        skip_user_btn = Button(
            text="Skip as User",
            size_hint=(0.5, 1),
            background_normal='',
            background_color=(0.22, 0.27, 0.74, 0.7),
            color=(1, 1, 1, 1),
            font_size=dp(14)
        )
        skip_admin_btn.bind(on_release=lambda instance: self.skip_login('admin'))
        skip_user_btn.bind(on_release=lambda instance: self.skip_login('user'))
        skip_btns_box.add_widget(skip_admin_btn)
        skip_btns_box.add_widget(skip_user_btn)
        form_box.add_widget(skip_btns_box)

        # Error message
        self.message = Label(
            text="",
            color=(0.9, 0.3, 0.3, 1),
            size_hint=(1, None),
            height=dp(30)
        )
        form_box.add_widget(self.message)

        # Info text
        info = Label(text="This is a secure system exclusively for POSit authorized personnel.\nFor account assistance, please contact your system administrator.", color=(0.5,0.5,0.5,1), font_size=dp(12), size_hint=(1, None), height=dp(40), halign='left', valign='top')
        info.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
        form_box.add_widget(info)

        right_panel.add_widget(form_box)

        right_panel.add_widget(Widget(size_hint_y=1))  # Bottom spacer

        root_layout.add_widget(right_panel)

        # Store focusable widgets for tab navigation
        self.focusables = [self.username, self.password, self.remember_checkbox, self.login_btn]
        for widget in self.focusables:
            if hasattr(widget, 'focus'):  # Only TextInput and Button have focus
                widget.focus = False

        # Bind keyboard events
        Window.bind(on_key_down=self._on_key_down)

        self.add_widget(root_layout)

    def _update_left_bg(self, instance, value):
        self.left_rect.size = instance.size
        self.left_rect.pos = instance.pos

    def _update_right_bg(self, instance, value):
        self.right_rect.size = instance.size
        self.right_rect.pos = instance.pos

    def _update_username_border(self, instance, value):
        self.username_border.pos = (self.username.x, self.username.y)
        self.username_border.size = (self.username.width, 1)

    def _update_password_border(self, instance, value):
        self.password_border.pos = (self.password.x, self.password.y)
        self.password_border.size = (self.password.width, 1)

    def _update_text_size(self, instance, value):
        instance.text_size = (instance.width, None)
        instance.texture_update()
        if instance.texture_size[1] > instance.height:
            instance.text_size = (instance.width, instance.height)

    def login(self, instance):
        uname = self.username.text
        pword = self.password.text
        role = auth.authUser(self.users, uname, pword)
        if role:
            auth.setUserSession(uname, role)
            self.message.text = f"Welcome {uname} ({role})"
            if role == "admin":
                self.manager.current = "admin_dashboard"
            else:
                self.manager.current = "user_dashboard"
        else:
            self.message.text = "Invalid credentials"

    def skip_login(self, role):
        uname = 'admin' if role == 'admin' else 'user'
        auth.setUserSession(uname, role)
        self.message.text = f"Welcome {uname} ({role})"
        if role == "admin":
            self.manager.current = "admin_dashboard"
        else:
            self.manager.current = "user_dashboard"

    def _on_key_down(self, window, key, scancode, codepoint, modifiers):
        # Tab key
        if key == 9:
            current = None
            for w in self.focusables:
                if hasattr(w, 'focus') and w.focus:
                    current = w
                    break
            if current in self.focusables:
                idx = self.focusables.index(current)
                next_idx = (idx + 1) % len(self.focusables)
            else:
                next_idx = 0
            next_widget = self.focusables[next_idx]
            if hasattr(next_widget, 'focus'):
                next_widget.focus = True
            return True  # Stop further handling
        # Enter key
        if key in (13, 271):  # 13=Enter, 271=Keypad Enter
            self.login_btn.trigger_action(duration=0.1)
            return True
        return False
            
        