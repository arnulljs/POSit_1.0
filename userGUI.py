from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock

# Global color definitions
normal_color = (0.22, 0.27, 0.74, 1)  # #3944BC in RGBA 
pressed_color = (0.18, 0.22, 0.64, 1)  # Slightly darker shade for pressed state
gray_bg = (0.95, 0.95, 0.97, 1)  # Light gray background
white = (1, 1, 1, 1)
black = (0, 0, 0, 1)

# Sample flight data
routes_data = [
    {"from": "Manila", "to": "Cebu", "economy_price": 3500, "business_price": 5800, "availability": True},
    {"from": "Cebu", "to": "Manila", "economy_price": 3500, "business_price": 5800, "availability": True},
    {"from": "Manila", "to": "Davao", "economy_price": 4200, "business_price": 6500, "availability": True},
    {"from": "Davao", "to": "Manila", "economy_price": 6500, "business_price": 9500, "availability": True},
    {"from": "Cebu", "to": "Davao", "economy_price": 2900, "business_price": 4800, "availability": True},
    {"from": "Davao", "to": "Cebu", "economy_price": 2900, "business_price": 4800, "availability": True},
    {"from": "Manila", "to": "Davao", "economy_price": 4200, "business_price": 6500, "availability": False},
]

class RouteSelector(BoxLayout):
    def __init__(self, **kwargs):
        super(RouteSelector, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(15)
        self.size_hint_y = None
        self.height = dp(800)  # Set appropriate height
        self.selected_routes = []
        
        # Add a white background with rounded corners
        with self.canvas.before:
            Color(*white)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(5)])
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        # Add filter tabs at the top
        self.add_filter_tabs()
        
        # Add route cards in a scrollview
        self.route_container = GridLayout(cols=1, spacing=dp(15), size_hint_y=None)
        self.route_container.bind(minimum_height=self.route_container.setter('height'))
        
        scrollview = ScrollView(size_hint=(1, 1))
        scrollview.add_widget(self.route_container)
        self.add_widget(scrollview)
        
        # Load routes
        self.load_routes(routes_data)
    
    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos
    
    def add_filter_tabs(self):
        tab_layout = BoxLayout(size_hint=(1, None), height=dp(50), spacing=dp(5))
        
        # Create tab buttons
        tabs = ["All Routes", "Manila-Cebu", "Cebu-Manila", "Manila-Davao", "Cebu-Davao", "Davao-Cebu", "Davao-Manila"]
        
        for i, tab in enumerate(tabs):
            btn = ToggleButton(
                text=tab,
                group="filter_tabs",
                size_hint=(1, 1),
                font_size=sp(14),
                background_normal="",
                background_down="",
                color=black if i > 0 else white,
                bold=False
            )
            
            # Customize appearance based on index
            if i == 0:  # First tab is selected
                btn.state = "down"
                with btn.canvas.before:
                    Color(*normal_color)
                    RoundedRectangle(size=btn.size, pos=btn.pos, radius=[dp(5)])
            else:
                with btn.canvas.before:
                    Color(0.9, 0.9, 0.9, 1)
                    RoundedRectangle(size=btn.size, pos=btn.pos, radius=[dp(5)])
            
            btn.bind(size=self._update_tab_bg, pos=self._update_tab_bg, state=self._update_tab_state)
            tab_layout.add_widget(btn)
        
        self.add_widget(tab_layout)
    
    def _update_tab_bg(self, instance, value):
        instance.canvas.before.clear()
        if instance.state == "down":
            with instance.canvas.before:
                Color(*normal_color)
                RoundedRectangle(size=instance.size, pos=instance.pos, radius=[dp(5)])
        else:
            with instance.canvas.before:
                Color(0.9, 0.9, 0.9, 1)
                RoundedRectangle(size=instance.size, pos=instance.pos, radius=[dp(5)])
    
    def _update_tab_state(self, instance, value):
        if value == "down":
            instance.color = white
        else:
            instance.color = black
    
    def load_routes(self, routes_data):
        self.route_container.clear_widgets()
        
        # Create a grid with 2 columns for route cards
        grid = GridLayout(cols=2, spacing=dp(15), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        for route in routes_data:
            # Create economy card
            economy_card = self.create_route_card(
                route["from"], 
                route["to"], 
                "Economy",
                route["economy_price"],
                route["availability"]
            )
            
            # Create business card
            business_card = self.create_route_card(
                route["from"], 
                route["to"], 
                "Business",
                route["business_price"],
                route["availability"]
            )
            
            grid.add_widget(economy_card)
            grid.add_widget(business_card)
        
        self.route_container.add_widget(grid)
    
    def create_route_card(self, from_city, to_city, travel_class, price, available=True):
        card = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(140),
            padding=dp(10)
        )
        
        # Create border based on travel class
        border_color = (0, 0.7, 0.7, 1) if travel_class == "Business" else (1, 0.7, 0, 1)
        
        with card.canvas.before:
            Color(*white)
            self.card_rect = RoundedRectangle(size=card.size, pos=card.pos, radius=[dp(8)])
            
            # Add border
            Color(*border_color)
            self.card_border = RoundedRectangle(
                size=card.size, pos=card.pos, radius=[dp(8)], 
                line_width=dp(1.5) if available else dp(0),
                width=dp(1.5) if available else dp(0)
            )
        
        card.bind(size=lambda obj, val: self._update_card_rect(obj, val, border_color, available), 
                 pos=lambda obj, val: self._update_card_rect(obj, val, border_color, available))
        
        # Add destination labels
        route_label = Label(
            text=f"{from_city}-{to_city}",
            font_size=sp(16),
            bold=True,
            color=black,
            size_hint=(1, None),
            height=dp(25),
            halign='left'
        )
        route_label.bind(size=self._update_label)
        
        # Add class label
        class_label = Label(
            text=f"{travel_class}",
            font_size=sp(14),
            color=border_color,
            size_hint=(1, None),
            height=dp(20),
            halign='left'
        )
        class_label.bind(size=self._update_label)
        
        # Add one-way label
        way_label = Label(
            text="One-way",
            font_size=sp(12),
            color=(0.5, 0.5, 0.5, 1),
            size_hint=(1, None),
            height=dp(20),
            halign='left'
        )
        way_label.bind(size=self._update_label)
        
        # Add price
        price_label = Label(
            text=f"₱{price:,}",
            font_size=sp(18),
            bold=True,
            color=normal_color if available else (0.6, 0.6, 0.6, 1),
            size_hint=(1, None),
            height=dp(25),
            halign='left'
        )
        price_label.bind(size=self._update_label)
        
        # For unavailable card, show "OUT OF STOCK"
        if not available:
            card.opacity = 0.7
            out_label = Label(
                text="OUT OF STOCK",
                font_size=sp(14),
                bold=True,
                color=(0.8, 0, 0, 1),
                size_hint=(1, None),
                height=dp(20),
                halign='center'
            )
            card.add_widget(route_label)
            card.add_widget(class_label)
            card.add_widget(way_label)
            card.add_widget(out_label)
        else:
            card.add_widget(route_label)
            card.add_widget(class_label)
            card.add_widget(way_label)
            card.add_widget(price_label)
            # Make card selectable
            card.bind(on_touch_down=lambda obj, touch: self.select_card(obj, touch, f"{from_city}-{to_city}", travel_class, price))
        
        return card
    
    def _update_label(self, instance, value):
        instance.text_size = (instance.width, None)
    
    def _update_card_rect(self, instance, value, border_color, available):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*white)
            RoundedRectangle(size=instance.size, pos=instance.pos, radius=[dp(8)])
            
            # Add border
            Color(*border_color)
            RoundedRectangle(
                size=instance.size, pos=instance.pos, radius=[dp(8)], 
                line_width=dp(1.5) if available else dp(0),
                width=dp(1.5) if available else dp(0)
            )
    
    def select_card(self, instance, touch, route, travel_class, price):
        if instance.collide_point(*touch.pos):
            # Here we would handle selection logic
            # For now, let's just highlight the card
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(*normal_color)
                RoundedRectangle(size=instance.size, pos=instance.pos, radius=[dp(8)])
            
            # Update labels to white
            for child in instance.children:
                if isinstance(child, Label):
                    child.color = white
            
            # Add to selected routes
            self.selected_routes.append({
                "route": route, 
                "class": travel_class, 
                "price": price
            })
            
            # In a real app, you'd update the transaction panel
            # For now, we'll simulate it with a delay
            Clock.schedule_once(lambda dt: self._reset_card(instance, route, travel_class, price), 0.3)
            return True
    
    def _reset_card(self, instance, route, travel_class, price):
        border_color = (0, 0.7, 0.7, 1) if travel_class == "Business" else (1, 0.7, 0, 1)
        
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*white)
            RoundedRectangle(size=instance.size, pos=instance.pos, radius=[dp(8)])
            
            # Add border
            Color(*border_color)
            RoundedRectangle(
                size=instance.size, pos=instance.pos, radius=[dp(8)], 
                line_width=dp(1.5),
                width=dp(1.5)
            )
        
        # Reset label colors
        for i, child in enumerate(instance.children):
            if isinstance(child, Label):
                if i == 0:  # Route name
                    child.color = black
                elif i == 1:  # Class label
                    child.color = border_color
                elif i == 2:  # One-way label
                    child.color = (0.5, 0.5, 0.5, 1)
                elif i == 3:  # Price label
                    child.color = normal_color


class TransactionPanel(BoxLayout):
    def __init__(self, **kwargs):
        super(TransactionPanel, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(15)
        self.padding = dp(15)
        self.size_hint_x = 0.25
        
        # Add a white background
        with self.canvas.before:
            Color(*white)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        # Transaction header
        header = Label(
            text="Current Transaction",
            font_size=sp(16),
            bold=True,
            size_hint=(1, None),
            height=dp(30),
            halign='left',
            color=black
        )
        header.bind(size=self._update_label)
        self.add_widget(header)
        
        # Transaction ID
        transaction_id = Label(
            text="#12458",
            font_size=sp(14),
            size_hint=(1, None),
            height=dp(20),
            halign='right',
            color=(0.5, 0.5, 0.5, 1)
        )
        transaction_id.bind(size=self._update_label)
        self.add_widget(transaction_id)
        
        # Sample items (this would be updated dynamically)
        self.items_container = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(150), spacing=dp(10))
        self.add_sample_items()
        self.add_widget(self.items_container)
        
        # Subtotal
        subtotal_layout = BoxLayout(size_hint=(1, None), height=dp(30))
        subtotal_label = Label(
            text="Subtotal",
            font_size=sp(14),
            size_hint=(0.5, 1),
            halign='left',
            color=black
        )
        subtotal_label.bind(size=self._update_label)
        
        subtotal_amount = Label(
            text="₱12,800",
            font_size=sp(14),
            size_hint=(0.5, 1),
            halign='right',
            color=black
        )
        subtotal_amount.bind(size=self._update_label)
        
        subtotal_layout.add_widget(subtotal_label)
        subtotal_layout.add_widget(subtotal_amount)
        self.add_widget(subtotal_layout)
        
        # Tax
        tax_layout = BoxLayout(size_hint=(1, None), height=dp(30))
        tax_label = Label(
            text="Tax (12%)",
            font_size=sp(14),
            size_hint=(0.5, 1),
            halign='left',
            color=black
        )
        tax_label.bind(size=self._update_label)
        
        tax_amount = Label(
            text="₱1,536",
            font_size=sp(14),
            size_hint=(0.5, 1),
            halign='right',
            color=black
        )
        tax_amount.bind(size=self._update_label)
        
        tax_layout.add_widget(tax_label)
        tax_layout.add_widget(tax_amount)
        self.add_widget(tax_layout)
        
        # Discount
        discount_layout = BoxLayout(size_hint=(1, None), height=dp(30))
        discount_label = Label(
            text="Discount",
            font_size=sp(14),
            size_hint=(0.5, 1),
            halign='left',
            color=black
        )
        discount_label.bind(size=self._update_label)
        
        discount_amount = Label(
            text="₱0",
            font_size=sp(14),
            size_hint=(0.5, 1),
            halign='right',
            color=black
        )
        discount_amount.bind(size=self._update_label)
        
        discount_layout.add_widget(discount_label)
        discount_layout.add_widget(discount_amount)
        self.add_widget(discount_layout)
        
        # Total with line above
        line = BoxLayout(size_hint=(1, None), height=dp(1))
        with line.canvas:
            Color(0.8, 0.8, 0.8, 1)
            Rectangle(size=line.size, pos=line.pos)
        line.bind(size=self._update_line, pos=self._update_line)
        self.add_widget(line)
        
        total_layout = BoxLayout(size_hint=(1, None), height=dp(40))
        total_label = Label(
            text="TOTAL",
            font_size=sp(16),
            bold=True,
            size_hint=(0.5, 1),
            halign='left',
            color=black
        )
        total_label.bind(size=self._update_label)
        
        total_amount = Label(
            text="₱14,336",
            font_size=sp(16),
            bold=True,
            size_hint=(0.5, 1),
            halign='right',
            color=black
        )
        total_amount.bind(size=self._update_label)
        
        total_layout.add_widget(total_label)
        total_layout.add_widget(total_amount)
        self.add_widget(total_layout)
        
        # Action buttons
        void_button = Button(
            text="Void Item",
            size_hint=(0.48, None),
            height=dp(40),
            background_normal="",
            background_color=(0.9, 0.9, 0.9, 1),
            color=black
        )
        
        price_check = Button(
            text="Price Check",
            size_hint=(0.48, None),
            height=dp(40),
            background_normal="",
            background_color=(0.9, 0.9, 0.9, 1),
            color=black
        )
        
        action_layout = BoxLayout(size_hint=(1, None), height=dp(40), spacing=dp(10))
        action_layout.add_widget(void_button)
        action_layout.add_widget(price_check)
        self.add_widget(action_layout)
        
        # Payment methods
        payment_layout = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(160), spacing=dp(10))
        
        # First row of payment buttons
        payment_row1 = BoxLayout(size_hint=(1, None), height=dp(50), spacing=dp(10))
        cash_btn = Button(
            text="Cash",
            size_hint=(0.5, 1),
            background_normal="",
            background_color=normal_color,
            color=white
        )
        card_btn = Button(
            text="Card",
            size_hint=(0.5, 1),
            background_normal="",
            background_color=(0.9, 0.9, 0.9, 1),
            color=black
        )
        payment_row1.add_widget(cash_btn)
        payment_row1.add_widget(card_btn)
        
        # Second row of payment buttons
        payment_row2 = BoxLayout(size_hint=(1, None), height=dp(50), spacing=dp(10))
        gcash_btn = Button(
            text="GCash",
            size_hint=(0.5, 1),
            background_normal="",
            background_color=(0.9, 0.9, 0.9, 1),
            color=black
        )
        maya_btn = Button(
            text="Maya",
            size_hint=(0.5, 1),
            background_normal="",
            background_color=(0.9, 0.9, 0.9, 1),
            color=black
        )
        payment_row2.add_widget(gcash_btn)
        payment_row2.add_widget(maya_btn)
        
        payment_layout.add_widget(payment_row1)
        payment_layout.add_widget(payment_row2)
        self.add_widget(payment_layout)
        
        # Numpad
        numpad_layout = GridLayout(cols=3, size_hint=(1, None), height=dp(200), spacing=dp(5))
        
        # Create numpad buttons
        buttons = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '00', '0', 'C']
        
        for btn_text in buttons:
            btn = Button(
                text=btn_text,
                font_size=sp(18),
                background_normal="",
                background_color=(0.95, 0.95, 0.95, 1),
                color=black
            )
            numpad_layout.add_widget(btn)
        
        self.add_widget(numpad_layout)
        
        # Bottom action buttons
        bottom_actions = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(150), spacing=dp(10))
        
        cancel_btn = Button(
            text="Cancel",
            size_hint=(1, None),
            height=dp(40),
            background_normal="",
            background_color=(0.9, 0.2, 0.2, 1),
            color=white
        )
        
        discount_btn = Button(
            text="Discount",
            size_hint=(1, None),
            height=dp(40),
            background_normal="",
            background_color=(1, 0.6, 0, 1),
            color=white
        )
        
        checkout_btn = Button(
            text="Checkout ₱14,336",
            size_hint=(1, None),
            height=dp(50),
            background_normal="",
            background_color=(0.2, 0.7, 0.4, 1),
            color=white,
            font_size=sp(16)
        )
        
        bottom_actions.add_widget(cancel_btn)
        bottom_actions.add_widget(discount_btn)
        bottom_actions.add_widget(checkout_btn)
        
        self.add_widget(bottom_actions)
    
    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos
    
    def _update_line(self, instance, value):
        instance.canvas.clear()
        with instance.canvas:
            Color(0.8, 0.8, 0.8, 1)
            Rectangle(size=instance.size, pos=instance.pos)
    
    def _update_label(self, instance, value):
        instance.text_size = (instance.width, None)
    
    def add_sample_items(self):
        # First item
        item1 = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(70))
        
        item1_header = BoxLayout(size_hint=(1, None), height=dp(25))
        item1_name = Label(
            text="Manila-Cebu",
            font_size=sp(14),
            bold=True,
            size_hint=(0.8, 1),
            halign='left',
            color=black
        )
        item1_name.bind(size=self._update_label)
        
        item1_qty = Label(
            text="x2",
            font_size=sp(14),
            size_hint=(0.2, 1),
            halign='right',
            color=black
        )
        item1_qty.bind(size=self._update_label)
        
        item1_header.add_widget(item1_name)
        item1_header.add_widget(item1_qty)
        
        item1_details = Label(
            text="Economy, One-way",
            font_size=sp(12),
            size_hint=(1, None),
            height=dp(15),
            halign='left',
            color=(0.5, 0.5, 0.5, 1)
        )
        item1_details.bind(size=self._update_label)
        
        item1_price = Label(
            text="₱3,500 each",
            font_size=sp(12),
            size_hint=(1, None),
            height=dp(15),
            halign='left',
            color=(0.5, 0.5, 0.5, 1)
        )
        item1_price.bind(size=self._update_label)
        
        item1.add_widget(item1_header)
        item1.add_widget(item1_details)
        item1.add_widget(item1_price)
        
        # Second item
        item2 = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(70))
        
        item2_header = BoxLayout(size_hint=(1, None), height=dp(25))
        item2_name = Label(
            text="Cebu-Manila",
            font_size=sp(14),
            bold=True,
            size_hint=(0.8, 1),
            halign='left',
            color=black
        )
        item2_name.bind(size=self._update_label)
        
        item2_qty = Label(
            text="x1",
            font_size=sp(14),
            size_hint=(0.2, 1),
            halign='right',
            color=black
        )
        item2_qty.bind(size=self._update_label)
        
        item2_header.add_widget(item2_name)
        item2_header.add_widget(item2_qty)
        
        item2_details = Label(
            text="Business, One-way",
            font_size=sp(12),
            size_hint=(1, None),
            height=dp(15),
            halign='left',
            color=(0.5, 0.5, 0.5, 1)
        )
        item2_details.bind(size=self._update_label)
        
        item2_price = Label(
            text="₱5,800 each",
            font_size=sp(12),
            size_hint=(1, None),
            height=dp(15),
            halign='left',
            color=(0.5, 0.5, 0.5, 1)
        )
        item2_price.bind(size=self._update_label)
        
        item2.add_widget(item2_header)
        item2.add_widget(item2_details)
        item2.add_widget(item2_price)
        
        self.items_container.add_widget(item1)
        self.items_container.add_widget(item2)


class NavBar(BoxLayout):
    def __init__(self, **kwargs):
        super(NavBar, self).__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(60)
        self.orientation = 'horizontal'
        
        # Left section - Logo and title
        left_section = BoxLayout(size_hint=(0.3, 1), orientation='horizontal')
        with left_section.canvas.before:
            Color(*normal_color)
            Rectangle(size=left_section.size, pos=left_section.pos)
        left_section.bind(size=self._update_left_bg, pos=self._update_left_bg)
        
        logo_btn = Button(
            text="POSH",
            size_hint=(None, 1),
            width=dp(100),
            background_normal="",
            background_color=normal_color,
            color=white,
            font_size=sp(16),
            bold=True
        )
        left_section.add_widget(logo_btn)
        
        # Spacer
        spacer = BoxLayout(size_hint=(0.7, 1))
        with spacer.canvas.before:
            Color(*normal_color)
            Rectangle(size=spacer.size, pos=spacer.pos)
        spacer.bind(size=self._update_spacer_bg, pos=self._update_spacer_bg)
        
        # Navigation tabs
        nav_tabs = BoxLayout(size_hint=(0.5, 1), padding=[dp(10), 0])
        with nav_tabs.canvas.before:
            Color(*white)
            Rectangle(size=nav_tabs.size, pos=nav_tabs.pos)
        nav_tabs.bind(size=self._update_tabs_bg, pos=self._update_tabs_bg)
        
        tab_items = ["Dashboard", "Inventory Management", "User Management", "Reports", "Settings"]
        
        for item in tab_items:
            tab = Button(
                text=item,
                size_hint=(1, 1),
                background_normal="",
                background_color=(1, 1, 1, 0),
                color=(0.5, 0.5, 0.5, 1) if item != "Dashboard" else normal_color,
                font_size=sp(14),
                bold=item == "Dashboard"
            )
            nav_tabs.add_widget(tab)
        
        # Right section - User avatar
        right_section = BoxLayout(size_hint=(0.2, 1), padding=[0, dp(10)])
        with right_section.canvas.before:
            Color(*white)
            Rectangle(size=right_section.size, pos=right_section.pos)
        right_section.bind(size=self._update_right_bg, pos=self._update_right_bg)
        
        # Add user info and icon
        user_layout = BoxLayout(size_hint=(1, 1), spacing=dp(10))
        
        user_info = BoxLayout(orientation='vertical', size_hint=(0.7, 1), padding=[dp(5), 0])
        user_name = Label(
            text="John Doe",
            font_size=sp(14),
            bold=True,
            size_hint=(1, 0.5),
            halign='right',
            color=black
        )
        user_name.bind(size=self._update_label)
        
        user_role = Label(
            text="Admin",
            font_size=sp(12),
            size_hint=(1, 0.5),
            halign='right',
            color=(0.5, 0.5, 0.5, 1)
        )
        user_role.bind(size=self._update_label)
        
        user_info.add_widget(user_name)
        user_info.add_widget(user_role)
        
        # Create avatar button (circle with initials)
        avatar_btn = Button(
            text="JD",
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            background_normal="",
            background_color=normal_color,
            color=white,
            font_size=sp(14),
            bold=True
        )
        
        # Make avatar circular
        with avatar_btn.canvas.before:
            Color(*normal_color)
            self.avatar_ellipse = Rectangle(size=avatar_btn.size, pos=avatar_btn.pos)
        avatar_btn.bind(size=self._update_avatar, pos=self._update_avatar)
        
        user_layout.add_widget(user_info)
        user_layout.add_widget(avatar_btn)
        right_section.add_widget(user_layout)
        
        # Combine all sections
        self.add_widget(left_section)
        self.add_widget(spacer)
        self.add_widget(nav_tabs)
        self.add_widget(right_section)
    
    def _update_left_bg(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*normal_color)
            Rectangle(size=instance.size, pos=instance.pos)
    
    def _update_spacer_bg(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*normal_color)
            Rectangle(size=instance.size, pos=instance.pos)
    
    def _update_tabs_bg(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*white)
            Rectangle(size=instance.size, pos=instance.pos)
    
    def _update_right_bg(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*white)
            Rectangle(size=instance.size, pos=instance.pos)
    
    def _update_label(self, instance, value):
        instance.text_size = (instance.width, None)
    
    def _update_avatar(self, instance, value):
        # Create circular avatar
        self.avatar_ellipse.size = instance.size
        self.avatar_ellipse.pos = instance.pos


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        
        # Create root layout
        root_layout = BoxLayout(orientation='vertical')
        
        # Add the navbar at the top
        navbar = NavBar()
        root_layout.add_widget(navbar)
        
        # Create content layout (horizontal)
        content_layout = BoxLayout(orientation='horizontal', padding=[dp(20), dp(20), dp(20), dp(20)], spacing=dp(20))
        
        # Set background color
        with content_layout.canvas.before:
            Color(*gray_bg)
            Rectangle(size=content_layout.size, pos=content_layout.pos)
        content_layout.bind(size=self._update_bg, pos=self._update_bg)
        
        # Add route selector (left side)
        route_selector = RouteSelector()
        content_layout.add_widget(route_selector)
        
        # Add transaction panel (right side)
        transaction_panel = TransactionPanel()
        content_layout.add_widget(transaction_panel)
        
        root_layout.add_widget(content_layout)
        self.add_widget(root_layout)
    
    def _update_bg(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*gray_bg)
            Rectangle(size=instance.size, pos=instance.pos)


class AirlineBookingApp(App):
    def build(self):
        # Set window size for desktop
        Window.size = (1280, 720)
        Window.minimum_width, Window.minimum_height = 1024, 680
        
        # Create screen manager
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        
        return sm


if __name__ == "__main__":
    AirlineBookingApp().run()