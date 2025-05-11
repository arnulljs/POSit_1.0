from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.popup import Popup

import auth
from models import User, Admin

ACCENT_BLUE = (0.22, 0.27, 0.74, 1)

class NavBar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(50)
        self.padding = [dp(10), 0, dp(10), 0]
        self.spacing = dp(20)
        with self.canvas.before:
            Color(*ACCENT_BLUE)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)
        self.build_navbar()

    def _update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def build_navbar(self):
        # Logo/Title
        logo = Label(text='[b]POSit[/b]', markup=True, font_size=dp(20), color=(1,1,1,1), size_hint_x=None, width=dp(120))
        self.add_widget(logo)

        # Navigation buttons
        nav_options = [
            ("Dashboard", self.goto_dashboard),
            ("Inventory Management", self.goto_inventory),
            ("Transaction View", self.goto_transaction),
            ("User Management", lambda *_: self.show_popup("User Management")),
            ("Reports", lambda *_: self.show_popup("Reports")),
            ("Settings", lambda *_: self.show_popup("Settings")),
        ]
        for name, callback in nav_options:
            btn = Button(
                text=name,
                size_hint_x=1,  # Make buttons expand/contract
                background_normal='',
                background_color=ACCENT_BLUE,
                color=(1,1,1,1),
                font_size=dp(14)
            )
            btn.bind(on_release=callback)
            self.add_widget(btn)

        # Spacer
        self.add_widget(BoxLayout())

        # User info
        user_label = Label(text='Administrator', font_size=dp(14), color=(1,1,1,1), size_hint_x=None, width=dp(120), halign='right')
        self.add_widget(user_label)
        avatar = Button(text='A', size_hint=(None, None), size=(dp(32), dp(32)), background_normal='', background_color=ACCENT_BLUE, color=(1,1,1,1), font_size=dp(16))
        self.add_widget(avatar)

    def show_popup(self, section):
        popup = Popup(title='Navigation',
                      content=Label(text=f'This would redirect to {section}.'),
                      size_hint=(None, None), size=(dp(300), dp(150)))
        popup.open()

    def get_screen_manager(self):
        parent = self.parent
        while parent:
            if isinstance(parent, ScreenManager):
                return parent
            parent = parent.parent
        return None

    def goto_dashboard(self, *_):
        sm = self.get_screen_manager()
        if sm:
            sm.current = 'admin_dashboard'

    def goto_inventory(self, *_):
        sm = self.get_screen_manager()
        if sm and not sm.has_screen('admin_inventory'):
            from adminInventory import AdminInventoryScreen  # Local import to avoid circular import
            sm.add_widget(AdminInventoryScreen(name='admin_inventory'))
        if sm:
            sm.current = 'admin_inventory'

    def goto_transaction(self, *_):
        sm = self.get_screen_manager()
        if sm:
            sm.current = 'user_dashboard'