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
from kivy.properties import NumericProperty, ListProperty, StringProperty, ObjectProperty
from kivy.animation import Animation
from kivy.uix.popup import Popup # Import Popup
from kivy.uix.textinput import TextInput # Import TextInput

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

# Define tax rate
TAX_RATE = 0.12

class QuantityPopup(Popup):
    # ObjectProperty to hold the transaction panel instance
    transaction_panel = ObjectProperty(None)
    # ObjectProperty to hold the item data
    item_data = ObjectProperty(None)

    def __init__(self, transaction_panel, item_data, **kwargs):
        super(QuantityPopup, self).__init__(**kwargs)
        self.transaction_panel = transaction_panel
        self.item_data = item_data
        self.title = 'Enter Quantity'
        self.size_hint = (0.6, 0.4) # Adjust size as needed

        # Layout for the popup content
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        # Label to show item name
        item_label = Label(text=f"Item: {item_data['route']} ({item_data['class']})",
                           size_hint_y=None, height=dp(30), color=black)
        content.add_widget(item_label)

        # TextInput for quantity
        self.quantity_input = TextInput(
            hint_text='Quantity',
            input_type='number',
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            font_size=sp(16),
            padding=[dp(10), dp(10), dp(10), dp(10)] # Adjust padding
        )
        content.add_widget(self.quantity_input)

        # Buttons for confirm and cancel
        button_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))

        confirm_button = Button(
            text='Add Item',
            background_normal="",
            background_color=(0.2, 0.7, 0.4, 1),
            color=white
        )
        confirm_button.bind(on_press=self.add_item_with_quantity)

        cancel_button = Button(
            text='Cancel',
            background_normal="",
            background_color=(0.9, 0.2, 0.2, 1),
            color=white
        )
        cancel_button.bind(on_press=self.dismiss)

        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)

        content.add_widget(button_layout)
        self.content = content

    def add_item_with_quantity(self, instance):
        try:
            quantity = int(self.quantity_input.text)
            if quantity > 0:
                # Call the method in TransactionPanel to add the item with quantity
                self.transaction_panel.add_item_to_transaction(self.item_data, quantity)
                self.dismiss() # Close the popup
            else:
                # Optionally show an error if quantity is not positive
                print("Quantity must be a positive number") # Replace with a proper error message
        except ValueError:
            # Optionally show an error if input is not a valid number
            print("Invalid quantity. Please enter a number.") # Replace with a proper error message

class RouteSelector(BoxLayout):
    # Modified __init__ to accept transaction_panel instance
    def __init__(self, transaction_panel, **kwargs):
        super(RouteSelector, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(15)
        self.size_hint_y = None
        self.height = dp(800)  # Set appropriate height
        self.transaction_panel = transaction_panel # Store the transaction panel instance

        # Add a white background with rounded corners
        with self.canvas.before:
            Color(*white)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(5)])
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Add filter tabs at the top
        self.add_filter_tabs()

        # Add route cards in a scrollview
        self.route_container = GridLayout(cols=2, spacing=dp(15), size_hint_y=None)
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

            self.route_container.add_widget(economy_card)
            self.route_container.add_widget(business_card)

    def create_route_card(self, from_city, to_city, travel_class, price, available=True):
        card = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(140),
            padding=dp(10)
        )

        # Create border based on travel class and store original color
        border_color = (0, 0.7, 0.7, 1) if travel_class == "Business" else (1, 0.7, 0, 1)
        card.original_border_color = border_color # Store original color

        with card.canvas.before:
            Color(*white)
            self.card_rect = RoundedRectangle(size=card.size, pos=card.pos, radius=[dp(8)])

            # Add border
            Color(*border_color, group='color_border') # Added group for animation
            # Store the border instruction for animation
            card.border_instruction = RoundedRectangle(
                size=card.size, pos=card.pos, radius=[dp(8)],
                line_width=dp(1.5) if available else dp(0),
                width=dp(1.5) if available else dp(0)
            )

        card.bind(size=lambda obj, val: self._update_card_rect(obj, val, obj.original_border_color, available),
                 pos=lambda obj, val: self._update_card_rect(obj, val, obj.original_border_color, available))

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
            card.bind(on_touch_down=lambda obj, touch: self.select_card(obj, touch, {"route": f"{from_city}-{to_city}", "class": travel_class, "price": price}))

        return card

    def _update_label(self, instance, value):
        instance.text_size = (instance.width, None)

    def _update_card_rect(self, instance, value, border_color, available):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*white)
            RoundedRectangle(size=instance.size, pos=instance.pos, radius=[dp(8)])

            # Add border
            Color(*border_color, group='color_border') # Added group for animation
            instance.border_instruction = RoundedRectangle(
                size=instance.size, pos=instance.pos, radius=[dp(8)],
                line_width=dp(1.5) if available else dp(0),
                width=dp(1.5) if available else dp(0)
            )

    # Modified select_card to open the quantity popup
    def select_card(self, instance, touch, item_data):
        if instance.collide_point(*touch.pos):
            # Trigger the pulse animation
            self.animate_card_pulse(instance, instance.original_border_color)
            # Open the quantity popup
            popup = QuantityPopup(transaction_panel=self.transaction_panel, item_data=item_data)
            popup.open()
            return True
        return False # Return False if touch is not within the card

    # Method to animate the card border color
    def animate_card_pulse(self, card_instance, original_color):
        # Create an animation that changes the border color
        animation = Animation(r=pressed_color[0], g=pressed_color[1], b=pressed_color[2], a=pressed_color[3], duration=0.1) + \
                    Animation(r=original_color[0], g=original_color[1], b=original_color[2], a=original_color[3], duration=0.3)
        # Apply the animation to the Color instruction associated with the border
        # Ensure the group 'color_border' is used to target the correct instruction
        color_instruction = None
        for instruction in card_instance.canvas.before.children:
            if isinstance(instruction, Color) and instruction.group == 'color_border':
                color_instruction = instruction
                break
        if color_instruction:
             animation.start(color_instruction)


class TransactionPanel(BoxLayout):
    # Added properties for transaction details
    subtotal = NumericProperty(0)
    tax = NumericProperty(0)
    total = NumericProperty(0)
    transaction_items = ListProperty([]) # List to hold selected items

    def __init__(self, **kwargs):
        super(TransactionPanel, self).__init__(**kwargs)
        self.orientation = 'vertical'
        # Decreased overall spacing for the TransactionPanel
        self.spacing = dp(5)
        self.padding = dp(15)
        # self.size_hint_x = 0.25 # Removed size_hint_x here, set in MainScreen

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

        # Transaction ID (static for now)
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

        # Container for dynamically added items
        self.items_container = BoxLayout(orientation='vertical', size_hint=(1, None), spacing=dp(10))
        # Bind height to children's minimum_height to allow scrolling if needed
        self.items_container.bind(minimum_height=self.items_container.setter('height'))

        # Add a ScrollView for the items_container
        items_scrollview = ScrollView(size_hint=(1, 1))
        items_scrollview.add_widget(self.items_container)
        self.add_widget(items_scrollview)

        # Spacer to push subsequent elements down
        self.add_widget(BoxLayout(size_hint_y=1)) # Flexible space

        # Subtotal, Tax, Discount, and TOTAL text and amounts (moved here, above payment methods)
        # Adjusted height for more compact look
        subtotal_layout = BoxLayout(size_hint=(1, None), height=dp(25))
        subtotal_label = Label(
            text="Subtotal",
            font_size=sp(14),
            size_hint=(0.5, 1),
            halign='left',
            color=black
        )
        subtotal_label.bind(size=self._update_label)

        self.subtotal_amount_label = Label(
            text=f"₱{self.subtotal:,.2f}",
            font_size=sp(14),
            size_hint=(0.5, 1),
            halign='right',
            color=black
        )
        self.subtotal_amount_label.bind(size=self._update_label)

        subtotal_layout.add_widget(subtotal_label)
        subtotal_layout.add_widget(self.subtotal_amount_label)
        self.add_widget(subtotal_layout)

        tax_layout = BoxLayout(size_hint=(1, None), height=dp(25)) # Adjusted height
        tax_label = Label(
            text=f"Tax ({TAX_RATE*100:.0f}%)",
            font_size=sp(14),
            size_hint=(0.5, 1),
            halign='left',
            color=black
        )
        tax_label.bind(size=self._update_label)

        self.tax_amount_label = Label(
            text=f"₱{self.tax:,.2f}",
            font_size=sp(14),
            size_hint=(0.5, 1),
            halign='right',
            color=black
        )
        self.tax_amount_label.bind(size=self._update_label)

        tax_layout.add_widget(tax_label)
        tax_layout.add_widget(self.tax_amount_label)
        self.add_widget(tax_layout)

        discount_layout = BoxLayout(size_hint=(1, None), height=dp(25)) # Adjusted height
        discount_label = Label(
            text="Discount",
            font_size=sp(14),
            size_hint=(0.5, 1),
            halign='left',
            color=black
        )
        discount_label.bind(size=self._update_label)

        discount_amount = Label(
            text="₱0.00",
            font_size=sp(14),
            size_hint=(0.5, 1),
            halign='right',
            color=black
        )
        discount_amount.bind(size=self._update_label)

        discount_layout.add_widget(discount_label)
        discount_layout.add_widget(discount_amount)
        self.add_widget(discount_layout)

        line = BoxLayout(size_hint=(1, None), height=dp(1))
        with line.canvas:
            Color(0.8, 0.8, 0.8, 1)
            Rectangle(size=line.size, pos=line.pos)
        line.bind(size=self._update_line, pos=self._update_line)
        self.add_widget(line)

        total_layout = BoxLayout(size_hint=(1, None), height=dp(35)) # Adjusted height
        total_label = Label(
            text="TOTAL",
            font_size=sp(16),
            bold=True,
            size_hint=(0.5, 1),
            halign='left',
            color=black
        )
        total_label.bind(size=self._update_label)

        self.total_amount_label = Label(
            text=f"₱{self.total:,.2f}",
            font_size=sp(16),
            bold=True,
            size_hint=(0.5, 1),
            halign='right',
            color=black
        )
        self.total_amount_label.bind(size=self._update_label)

        total_layout.add_widget(total_label)
        total_layout.add_widget(self.total_amount_label)
        self.add_widget(total_layout)


        # Payment methods (kept above numpad)
        # Decreased height of payment_layout and payment rows
        payment_layout = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(80), spacing=dp(10))

        # First row of payment buttons
        payment_row1 = BoxLayout(size_hint=(1, None), height=dp(30), spacing=dp(10))
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
        payment_row2 = BoxLayout(size_hint=(1, None), height=dp(30), spacing=dp(10))
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
        numpad_layout = GridLayout(cols=3, size_hint=(1, None), height=dp(120), spacing=dp(5))

        # Create numpad buttons
        buttons = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '00', '0', 'C']

        for btn_text in buttons:
            btn = Button(
                text=btn_text,
                font_size=sp(18),
                background_normal="",
                background_color=(0.95, 0.95, 0.95, 1),
                color=black,
                size_hint_y=None, # Allow height to be set explicitly
                height=dp(30) # Set button height to match payment buttons
            )
            numpad_layout.add_widget(btn)

        self.add_widget(numpad_layout)

        # Bottom action buttons (Cancel, Discount, Checkout)
        bottom_actions = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(100), spacing=dp(10))

        cancel_discount_layout = BoxLayout(size_hint=(1, None), height=dp(40), spacing=dp(10))
        cancel_btn = Button(
            text="Cancel",
            size_hint=(0.5, None),
            height=dp(40),
            background_normal="",
            background_color=(0.9, 0.2, 0.2, 1),
            color=white
        )
        discount_btn = Button(
            text="Discount",
            size_hint=(0.5, None),
            height=dp(40),
            background_normal="",
            background_color=(1, 0.6, 0, 1),
            color=white
        )
        cancel_discount_layout.add_widget(cancel_btn)
        cancel_discount_layout.add_widget(discount_btn)

        self.checkout_btn = Button(
            text=f"Checkout ₱{self.total:,.2f}",
            size_hint=(1, None),
            height=dp(50),
            background_normal="",
            background_color=(0.2, 0.7, 0.4, 1),
            color=white,
            font_size=sp(16)
        )

        bottom_actions.add_widget(cancel_discount_layout)
        bottom_actions.add_widget(self.checkout_btn)

        self.add_widget(bottom_actions)


        # Initial total calculation and display update
        self.calculate_totals()
        self.update_total_display()

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

    # Method to add an item to the transaction with a specified quantity
    def add_item_to_transaction(self, item_data, quantity):
        # Check if the item is already in the list
        found = False
        for item in self.transaction_items:
            if item['route'] == item_data['route'] and item['class'] == item_data['class']:
                item['quantity'] += quantity # Add the specified quantity
                found = True
                break

        if not found:
            item_data['quantity'] = quantity # Set the initial quantity
            # Append to a temporary list first to trigger ListProperty observer
            temp_items = self.transaction_items[:]
            temp_items.append(item_data)
            self.transaction_items = temp_items
        else:
             # If item was found and quantity updated, need to trigger update manually for ListProperty
             self.transaction_items = self.transaction_items[:]


        self.update_items_display()
        self.calculate_totals()
        self.update_total_display()

    # Method to update the display of items in the transaction panel
    def update_items_display(self):
        self.items_container.clear_widgets()
        for item in self.transaction_items:
            item_widget = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(70))

            item_header = BoxLayout(size_hint=(1, None), height=dp(25))
            item_name = Label(
                text=item['route'],
                font_size=sp(14),
                bold=True,
                size_hint=(0.8, 1),
                halign='left',
                color=black
            )
            item_name.bind(size=self._update_label)

            item_qty = Label(
                text=f"x{item['quantity']}",
                font_size=sp(14),
                size_hint=(0.2, 1),
                halign='right',
                color=black
            )
            item_qty.bind(size=self._update_label)

            item_header.add_widget(item_name)
            item_header.add_widget(item_qty)

            item_details = Label(
                text=f"{item['class']}, One-way",
                font_size=sp(12),
                size_hint=(1, None),
                height=dp(15),
                halign='left',
                color=(0.5, 0.5, 0.5, 1)
            )
            item_details.bind(size=self._update_label)

            item_price_each = item['price'] # Assuming price in data is per item
            item_price_label = Label(
                text=f"₱{item_price_each:,.2f} each",
                font_size=sp(12),
                size_hint=(1, None),
                height=dp(15),
                halign='left',
                color=(0.5, 0.5, 0.5, 1)
            )
            item_price_label.bind(size=self._update_label)


            item_widget.add_widget(item_header)
            item_widget.add_widget(item_details)
            item_widget.add_widget(item_price_label)

            self.items_container.add_widget(item_widget)

    # Method to calculate subtotal, tax, and total
    def calculate_totals(self):
        self.subtotal = sum(item['price'] * item['quantity'] for item in self.transaction_items)
        self.tax = self.subtotal * TAX_RATE
        # Assuming no discount is applied for now
        self.total = self.subtotal + self.tax

    # Method to update the display of the total amounts
    def update_total_display(self):
        self.subtotal_amount_label.text = f"₱{self.subtotal:,.2f}"
        self.tax_amount_label.text = f"₱{self.tax:,.2f}"
        self.total_amount_label.text = f"₱{self.total:,.2f}"
        self.checkout_btn.text = f"Checkout ₱{self.total:,.2f}"


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

        # Add route selector (left side) - pass transaction_panel instance
        route_selector = RouteSelector(transaction_panel=None, size_hint_x=0.75) # Temporarily set transaction_panel to None
        content_layout.add_widget(route_selector)

        # Add transaction panel (right side) - instantiate first
        transaction_panel = TransactionPanel(size_hint_x=0.25)
        content_layout.add_widget(transaction_panel)

        # Now that transaction_panel is created, set it for route_selector
        route_selector.transaction_panel = transaction_panel


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
