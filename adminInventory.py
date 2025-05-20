from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from tickets import get_routes, add_route, remove_route, update_route, get_next_ticket_id
from adminNav import NavBar
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.spinner import Spinner

ACCENT_BLUE = (0.22, 0.27, 0.74, 1)
ROW_ALT_GRAY = (0.96, 0.96, 0.96, 1)
LIGHT_GRAY_BG = (0.95, 0.95, 0.95, 1)
WHITE = (1, 1, 1, 1)

class IconButton(ButtonBehavior, Image):
    pass

class TicketEditPopup(Popup):
    def __init__(self, ticket=None, on_save=None, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Edit Ticket' if ticket else 'Add New Item'
        self.size_hint = (0.5, 0.7)
        self.ticket = ticket or {}
        self.on_save = on_save

        self.original_event_hint = 'Event'
        self.original_price_hint = 'Price'
        self.original_avail_hint = 'Available'
        self.default_hint_text_color = (0,0,0,0.5) # Standard Kivy hint text color
        
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Fields
        self.ticket_id_input = TextInput(
            text=self.ticket.get('ticket_id', get_next_ticket_id()),
            hint_text='Ticket ID', multiline=False, readonly=True,
            size_hint_y=None, height=dp(40)
        )
        self.event_input = TextInput(text=self.ticket.get('event', ''), 
                                    hint_text=self.original_event_hint, multiline=False,
                                    size_hint_y=None, height=dp(40),
                                    hint_text_color=self.default_hint_text_color)
        # Tier as Spinner (dropdown)
        self.tier_input = Spinner(
            text=self.ticket.get('tier', 'Standard Seating'),
            values=['Standard Seating', 'Silver Seating', 'Gold Seating'],
            size_hint_y=None,
            height=dp(44) # Spinners often need a bit more height
        )
        self.price_input = TextInput(text=str(self.ticket.get('price', '')), 
                                    hint_text=self.original_price_hint, multiline=False,
                                    input_filter='int', size_hint_y=None, height=dp(40),
                                    hint_text_color=self.default_hint_text_color)
        self.avail_input = TextInput(text=str(self.ticket.get('availability', '')), 
                                    hint_text=self.original_avail_hint, multiline=False,
                                    input_filter='int', size_hint_y=None, height=dp(40),
                                    hint_text_color=self.default_hint_text_color)
        
        # Using Labels as simple text descriptors above inputs
        layout.add_widget(Label(text='Ticket ID', size_hint_y=None, height=dp(20), halign='left', color=(0,0,0,0.8)))
        layout.add_widget(self.ticket_id_input)
        layout.add_widget(Label(text='Event', size_hint_y=None, height=dp(20), halign='left', color=(0,0,0,0.8)))
        layout.add_widget(self.event_input)
        layout.add_widget(Label(text='Tier', size_hint_y=None, height=dp(20), halign='left', color=(0,0,0,0.8)))
        layout.add_widget(self.tier_input)
        layout.add_widget(Label(text='Price (₱)', size_hint_y=None, height=dp(20), halign='left', color=(0,0,0,0.8)))
        layout.add_widget(self.price_input)
        layout.add_widget(Label(text='Available', size_hint_y=None, height=dp(20), halign='left', color=(0,0,0,0.8)))
        layout.add_widget(self.avail_input)
        
        # Buttons
        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        save_btn = Button(text='Save', on_release=self.save)
        cancel_btn = Button(text='Cancel', on_release=lambda x: self.dismiss())
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        layout.add_widget(btn_layout)
        
        self.content = layout
        
    def save(self, instance):
        event_text = self.event_input.text.strip()
        price_text = self.price_input.text.strip()
        avail_text = self.avail_input.text.strip()
        
        # Reset hints first
        self.event_input.hint_text = self.original_event_hint
        self.event_input.hint_text_color = self.default_hint_text_color
        self.price_input.hint_text = self.original_price_hint
        self.price_input.hint_text_color = self.default_hint_text_color
        self.avail_input.hint_text = self.original_avail_hint
        self.avail_input.hint_text_color = self.default_hint_text_color

        # Validate inputs
        validation_passed = True
        if not event_text:
            self.event_input.hint_text = "Event cannot be empty."
            self.event_input.hint_text_color = (1, 0, 0, 1) # Red
            self.event_input.text = "" # Clear invalid input
            validation_passed = False
        
        if not price_text:
            self.price_input.hint_text = "Price cannot be empty."
            self.price_input.hint_text_color = (1, 0, 0, 1) # Red
            self.price_input.text = "" # Clear invalid input
            validation_passed = False
            
        if not avail_text:
            self.avail_input.hint_text = "Availability cannot be empty."
            self.avail_input.hint_text_color = (1, 0, 0, 1) # Red
            self.avail_input.text = "" # Clear invalid input
            validation_passed = False

        # If initial empty checks failed, return now
        if not validation_passed:
            return

        # Tier 2: Validate numeric inputs are greater than 0
        price_val = 0
        avail_val = 0

        if price_text: # Only proceed if not empty from previous check
            try:
                price_val = int(price_text)
                if price_val <= 0:
                    self.price_input.hint_text = "Price must be greater than 0."
                    self.price_input.hint_text_color = (1, 0, 0, 1) # Red
                    self.price_input.text = "" # Clear invalid input
                    validation_passed = False
            except ValueError: # Should be caught by input_filter, but good to have
                self.price_input.hint_text = "Price must be a whole number."
                self.price_input.hint_text_color = (1, 0, 0, 1) # Red
                self.price_input.text = "" # Clear invalid input
                validation_passed = False
        
        if avail_text: # Only proceed if not empty from previous check
            try:
                avail_val = int(avail_text)
                if avail_val <= 0: # Availability can be 0 if out of stock, but for adding/editing new stock, usually > 0. Let's assume >0 for this validation.
                    self.avail_input.hint_text = "Availability must be greater than 0."
                    self.avail_input.hint_text_color = (1, 0, 0, 1) # Red
                    self.avail_input.text = "" # Clear invalid input
                    validation_passed = False
            except ValueError:
                self.avail_input.hint_text = "Availability must be a whole number."
                self.avail_input.hint_text_color = (1, 0, 0, 1) # Red
                self.avail_input.text = "" # Clear invalid input
                validation_passed = False

        if not validation_passed:
            return

        data = {
            'ticket_id': self.ticket_id_input.text.strip(),
            'event': event_text,
            'tier': self.tier_input.text.strip(),
            'price': price_val,
            'availability': avail_val,
        }
        if self.on_save:
            self.on_save(data)
        self.dismiss()

class InventoryTable(BoxLayout):
    def __init__(self, parent_screen=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 0
        self.padding = 0
        self._rows = []
        self._current_page = 0
        self._items_per_page = 20
        self._total_items = 0
        self._search_query = ""
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        self.parent_screen = parent_screen
        
    def refresh_data(self, routes, query=""):
        self._search_query = query.lower()
        self._rows = [ticket for ticket in routes if 
                     not query or
                     query in ticket['ticket_id'].lower() or 
                     query in ticket['event'].lower() or 
                     query in ticket['tier'].lower()]
        self._total_items = len(self._rows)
        self._current_page = 0
        self.clear_widgets()
        self._load_current_page()
        
    def _load_current_page(self):
        start_idx = self._current_page * self._items_per_page
        end_idx = min(start_idx + self._items_per_page, self._total_items)
        
        # Pre-calculate row backgrounds
        row_bg = [(1, 1, 1, 1), ROW_ALT_GRAY]
        
        for idx in range(start_idx, end_idx):
            ticket = self._rows[idx]
            current_bg = row_bg[idx % 2]
            
            # Create row container (horizontal)
            row = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(40))
            with row.canvas.before:
                Color(*current_bg)
                row.bg_rect = Rectangle(size=row.size, pos=row.pos)
            row.bind(size=self._update_row_bg, pos=self._update_row_bg)

            # Add cells (7 columns)
            row.add_widget(Label(text=str(ticket['ticket_id']), color=(0, 0, 0, 0.8), size_hint=(1, 1)))
            row.add_widget(Label(text=str(ticket['event']), color=(0, 0, 0, 0.8), size_hint=(1, 1)))
            row.add_widget(Label(text=str(ticket['tier']), color=(0, 0, 0, 0.8), size_hint=(1, 1)))
            row.add_widget(Label(text=f"{ticket['price']:,}", color=(0, 0, 0, 0.8), size_hint=(1, 1)))
            row.add_widget(Label(text=str(ticket['availability']), color=(0, 0, 0, 0.8), size_hint=(1, 1)))
            row.add_widget(Label(text=str(ticket.get('created_at', 'N/A')), color=(0, 0, 0, 0.8), size_hint=(1, 1)))

            # Actions cell (center icons vertically and horizontally)
            actions = BoxLayout(size_hint=(1, 1), orientation='vertical', padding=[0, 0, 0, 0])
            icons = BoxLayout(
                orientation='horizontal',
                spacing=dp(6),
                size_hint=(None, None),
                width=dp(84),
                height=dp(24),
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            edit_btn = IconButton(source='icons/edit.png', size_hint=(None, None), width=dp(24), height=dp(24))
            edit_btn.bind(on_release=lambda btn, tid=ticket['ticket_id']: self.parent_screen.open_edit_popup(tid) if self.parent_screen else None)
            del_btn = IconButton(source='icons/delete.png', size_hint=(None, None), width=dp(24), height=dp(24))
            del_btn.bind(on_release=lambda btn, tid=ticket['ticket_id']: self.parent_screen.delete_ticket(tid) if self.parent_screen else None)
            add_stock_btn = Button(
                text='+',
                font_size=dp(16),
                bold=True,
                color=ACCENT_BLUE,
                size_hint=(None, None),
                width=dp(24),
                height=dp(24),
                background_normal='',
                background_color=(0, 0, 0, 0)
            )
            add_stock_btn.bind(on_release=lambda btn, tid=ticket['ticket_id']: self.parent_screen.increase_stock(tid) if self.parent_screen else None)
            icons.add_widget(edit_btn)
            icons.add_widget(del_btn)
            icons.add_widget(add_stock_btn)
            # Center icons in the actions cell
            actions.add_widget(Widget(size_hint_y=1))  # Top spacer
            actions.add_widget(icons)
            actions.add_widget(Widget(size_hint_y=1))  # Bottom spacer
            row.add_widget(actions)

            self.add_widget(row)
    
    def _update_row_bg(self, instance, value):
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.size = instance.size
            instance.bg_rect.pos = instance.pos
    
    def next_page(self):
        if (self._current_page + 1) * self._items_per_page < self._total_items:
            self._current_page += 1
            self.clear_widgets()
            self._load_current_page()
    
    def prev_page(self):
        if self._current_page > 0:
            self._current_page -= 1
            self.clear_widgets()
            self._load_current_page()

class AdminInventoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set background color to LIGHT_GRAY_BG at the Screen level
        with self.canvas.before:
            Color(*LIGHT_GRAY_BG)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)
        
        # Main layout (no background color here)
        self.layout = BoxLayout(orientation='vertical')
        
        # Add NavBar at the top
        self.layout.add_widget(NavBar())
        
        # Content area (no white background, just padding and spacing)
        content_area = BoxLayout(orientation='vertical', padding=[dp(32), dp(32), dp(32), dp(32)], spacing=dp(24), size_hint=(1, 1))
        
        # Title and subtitle
        title_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(60))
        title = Label(text='Inventory Management', font_size=20, bold=True, 
                     color=(0, 0, 0, 1), halign='left', valign='bottom', 
                     size_hint_y=None, height=dp(30))
        title.bind(texture_size=title.setter('texture_size'))
        title_layout.add_widget(title)
        
        subtitle = Label(text='Add, modify and manage ticket inventory', font_size=14, 
                        color=(0, 0, 0, 0.6), halign='left', valign='top', 
                        size_hint_y=None, height=dp(30))
        subtitle.bind(texture_size=subtitle.setter('texture_size'))
        title_layout.add_widget(subtitle)
        content_area.add_widget(title_layout)
        
        # Search and action bar
        action_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        
        # Search box
        self.search_input = TextInput(
            hint_text='Search inventory...',
            multiline=False,
            size_hint_x=1,
            background_normal='',
            background_active='',
            background_color=(0, 0, 0, 0),
            foreground_color=(0, 0, 0, 1),
            padding=[dp(5), dp(10), dp(5), dp(10)]
        )
        with self.search_input.canvas.after:
            Color(0, 0, 0, 1)
            self._search_border_line = Line(points=[], width=1.2)
        self.search_input.bind(pos=self._update_search_border, size=self._update_search_border)
        action_bar.add_widget(self.search_input)
        
        # Add New Item button (blue)
        add_btn = Button(
            text='+ Add New Item',
            size_hint_x=None,
            width=dp(120),
            background_normal='',
            background_color=ACCENT_BLUE,
            color=(1, 1, 1, 1)
        )
        def on_add_btn_press(instance):
            instance.background_color = (0.16, 0.20, 0.55, 1)
        def on_add_btn_release(instance):
            instance.background_color = ACCENT_BLUE
        add_btn.bind(on_press=on_add_btn_press, on_release=on_add_btn_release)
        add_btn.bind(on_release=self.open_add_popup)
        action_bar.add_widget(add_btn)
        
        content_area.add_widget(action_bar)
        
        # Table in a white rounded rectangle card
        from kivy.uix.boxlayout import BoxLayout as KivyBoxLayout
        table_card = KivyBoxLayout(orientation='vertical', size_hint=(1, 1), padding=[dp(16), dp(16), dp(16), dp(16)], spacing=dp(0))
        with table_card.canvas.before:
            Color(*WHITE)
            table_card.bg_rect = RoundedRectangle(size=table_card.size, pos=table_card.pos, radius=[(dp(16), dp(16))] * 4)
        table_card.bind(size=lambda instance, value: setattr(instance.bg_rect, 'size', instance.size))
        table_card.bind(pos=lambda instance, value: setattr(instance.bg_rect, 'pos', instance.pos))
        
        # Add table header
        header = BoxLayout(size_hint=(1, None), height=dp(40))
        headers = ['Ticket ID', 'Event', 'Tier', 'Price', 'Available', 'Created At', 'Actions']
        for header_text in headers:
            header.add_widget(Label(
                text=header_text,
                color=(0, 0, 0, 0.8),
                bold=True,
                size_hint=(1, 1)
            ))
        table_card.add_widget(header)
        
        # Table body (scrollable)
        self.scroll = ScrollView(size_hint=(1, 1))
        self.table = InventoryTable(parent_screen=self, size_hint_y=None)
        self.table.bind(minimum_height=self.table.setter('height'))
        self.scroll.add_widget(self.table)
        table_card.add_widget(self.scroll)
        
        content_area.add_widget(table_card)
        self.layout.add_widget(content_area)
        
        self.add_widget(self.layout)
        self.refresh_table()
        self.search_input.bind(text=lambda *_: self.refresh_table())

    def _update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos
        
    def _update_search_border(self, instance, value):
        self._search_border_line.points = [
            instance.x, instance.y,
            instance.x + instance.width, instance.y
        ]

    def refresh_table(self):
        routes = get_routes()
        query = self.search_input.text.strip()
        self.table.refresh_data(routes, query)

    def open_edit_popup(self, ticket_id_to_edit):
        current_routes = get_routes()
        ticket_to_edit_data = None
        for t_obj in current_routes:
            if t_obj['ticket_id'] == ticket_id_to_edit:
                ticket_to_edit_data = t_obj
                break
        
        if ticket_to_edit_data is None:
            print(f"Error: Ticket with ID {ticket_id_to_edit} not found for editing.")
            self.refresh_table() # Refresh to show current state
            return

        def save_callback(data):
            # Re-find index before updating, as list might have changed
            idx_for_update = -1
            fresh_routes_before_update = get_routes()
            for i, t_upd in enumerate(fresh_routes_before_update):
                if t_upd['ticket_id'] == ticket_id_to_edit: # Use original ticket_id_to_edit
                    idx_for_update = i
                    break
            
            if idx_for_update != -1:
                # data['ticket_id'] should match ticket_id_to_edit as it's readonly
                update_route(idx_for_update, data)
            else:
                print(f"Error: Ticket with ID {ticket_id_to_edit} disappeared before saving edit.")
            self.refresh_table()
            
        TicketEditPopup(ticket=ticket_to_edit_data.copy(), on_save=save_callback).open() # Pass a copy
    
    def open_add_popup(self, instance):
        def save_callback(data):
            add_route(data)
            self.refresh_table()
        TicketEditPopup(ticket=None, on_save=save_callback).open()
    
    def delete_ticket(self, ticket_id_to_delete):
        current_routes = get_routes()
        idx_to_delete = -1
        for i, ticket_obj in enumerate(current_routes):
            if ticket_obj['ticket_id'] == ticket_id_to_delete:
                idx_to_delete = i
                break
        
        if idx_to_delete != -1:
            remove_route(idx_to_delete)
            self.refresh_table()
        else:
            print(f"Warning: Ticket ID {ticket_id_to_delete} not found for deletion. Already deleted?")
            self.refresh_table() # Refresh to sync UI
    
    def increase_stock(self, ticket_id_to_modify):
        current_routes = get_routes()
        idx_to_modify = -1
        ticket_data_to_modify = None
        for i, ticket_obj in enumerate(current_routes):
            if ticket_obj['ticket_id'] == ticket_id_to_modify:
                idx_to_modify = i
                ticket_data_to_modify = ticket_obj
                break
        
        if ticket_data_to_modify is not None and idx_to_modify != -1:
            # Create a new dictionary for the update to ensure `update_route` gets fresh data
            updated_ticket_data = ticket_data_to_modify.copy()
            updated_ticket_data['availability'] += 1
            update_route(idx_to_modify, updated_ticket_data)
            self.refresh_table()
        else:
            print(f"Warning: Ticket ID {ticket_id_to_modify} not found for stock increase.")
            self.refresh_table()