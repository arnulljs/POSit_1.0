from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
import auth

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
            ("Transactions", self.goto_transaction),
            ("Reports", self.goto_reports),
        ]
        for name, callback in nav_options:
            btn = Button(text=name, size_hint_x=1, background_normal='', background_color=ACCENT_BLUE, color=(1,1,1,1), font_size=dp(14))
            btn.bind(on_release=callback)
            self.add_widget(btn)

        # Spacer
        self.add_widget(BoxLayout())

        # User info with dropdown
        from kivy.uix.boxlayout import BoxLayout as KivyBoxLayout
        current_user = auth.getCurrentUser()
        username = current_user.get('username', 'User') or 'User'
        user_box = KivyBoxLayout(orientation='horizontal', size_hint_x=None, width=dp(150), spacing=dp(8), pos_hint={'center_y': 0.5})
        user_btn = Button(
            text=username,
            size_hint=(None, None),
            size=(dp(90), dp(32)),
            background_normal='',
            background_color=ACCENT_BLUE,
            color=(1,1,1,1),
            font_size=dp(14),
            pos_hint={'center_y': 0.5}
        )
        avatar_btn = Button(
            text='U',
            size_hint=(None, None),
            size=(dp(32), dp(32)),
            background_normal='',
            background_color=ACCENT_BLUE,
            color=(1,1,1,1),
            font_size=dp(16),
            pos_hint={'center_y': 0.5}
        )
        # Dropdown for logout
        dropdown = DropDown()
        logout_btn = Button(text='Log out', size_hint_y=None, height=dp(40), background_normal='', background_color=(1,0.3,0.3,1), color=(1,1,1,1))
        logout_btn.bind(on_release=lambda *a: self.logout(dropdown))
        dropdown.add_widget(logout_btn)
        def open_dropdown(instance):
            dropdown.open(instance)
        user_btn.bind(on_release=open_dropdown)
        user_box.add_widget(user_btn)
        user_box.add_widget(avatar_btn)
        self.add_widget(user_box)

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

    def goto_transaction(self, *_):
        sm = self.get_screen_manager()
        if sm:
            sm.current = 'user_dashboard'

    def goto_reports(self, *_):
        sm = self.get_screen_manager()
        if sm and not sm.has_screen('reports_screen'):
            from reportsGUI import ReportScreen # Local import
            sm.add_widget(ReportScreen(name='reports_screen'))
        if sm:
            sm.current = 'reports_screen'

    def logout(self, dropdown):
        dropdown.dismiss()
        auth.logout()
        sm = self.get_screen_manager()
        if sm:
            sm.current = 'login'