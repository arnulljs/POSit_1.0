from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.uix.popup import Popup

ACCENT_BLUE = (0.22, 0.27, 0.74, 1)

class UserNavBar(BoxLayout):
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
            ("Transaction View", self.goto_transaction),
            ("Inventory Management", self.goto_inventory),
            ("Reports", lambda *_: self.show_popup("Reports")),
            ("Settings", lambda *_: self.show_popup("Settings")),
        ]
        for name, callback in nav_options:
            btn = Button(text=name, size_hint_x=None, width=dp(180), background_normal='', background_color=ACCENT_BLUE, color=(1,1,1,1), font_size=dp(14))
            btn.bind(on_release=callback)
            self.add_widget(btn)

        # Spacer
        self.add_widget(BoxLayout())

        # User info
        user_label = Label(text='User', font_size=dp(14), color=(1,1,1,1), size_hint_x=None, width=dp(120), halign='right')
        self.add_widget(user_label)
        avatar = Button(text='U', size_hint=(None, None), size=(dp(32), dp(32)), background_normal='', background_color=ACCENT_BLUE, color=(1,1,1,1), font_size=dp(16))
        self.add_widget(avatar)

    def show_popup(self, section):
        popup = Popup(title='Navigation',
                      content=Label(text=f'This would redirect to {section}.'),
                      size_hint=(None, None), size=(dp(300), dp(150)))
        popup.open()

    def get_screen_manager(self):
        parent = self.parent
        while parent:
            from kivy.uix.screenmanager import ScreenManager
            if isinstance(parent, ScreenManager):
                return parent
            parent = parent.parent
        return None

    def goto_inventory(self, *_):
        sm = self.get_screen_manager()
        if sm and not sm.has_screen('user_inventory'):
            # You can define and import UserInventoryScreen as needed
            pass  # Placeholder for actual screen addition
        if sm:
            sm.current = 'user_inventory'

    def goto_transaction(self, *_):
        sm = self.get_screen_manager()
        if sm:
            sm.current = 'user_dashboard'
