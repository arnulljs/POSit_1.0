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
        
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Fields
        self.ticket_id_input = TextInput(
            text=self.ticket.get('ticket_id', get_next_ticket_id()),
            hint_text='Ticket ID', multiline=False, readonly=True
        )
        self.event_input = TextInput(text=self.ticket.get('event', ''), 
                                    hint_text='Event', multiline=False)
        # Tier as Spinner (dropdown)
        self.tier_input = Spinner(
            text=self.ticket.get('tier', 'Standard Seating'),
            values=['Standard Seating', 'Silver Seating', 'Gold Seating'],
            size_hint_y=None,
            height=dp(40)
        )
        self.price_input = TextInput(text=str(self.ticket.get('price', '')), 
                                    hint_text='Price', multiline=False, 
                                    input_filter='int')
        self.avail_input = TextInput(text=str(self.ticket.get('availability', '')), 
                                    hint_text='Available', multiline=False, 
                                    input_filter='int')
        
        layout.add_widget(Label(text='Ticket ID'))
        layout.add_widget(self.ticket_id_input)
        layout.add_widget(Label(text='Event'))
        layout.add_widget(self.event_input)
        layout.add_widget(Label(text='Tier'))
        layout.add_widget(self.tier_input)
        layout.add_widget(Label(text='Price (₱)'))
        layout.add_widget(self.price_input)
        layout.add_widget(Label(text='Available'))
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
        data = {
            'ticket_id': self.ticket_id_input.text.strip(),
            'event': self.event_input.text.strip(),
            'tier': self.tier_input.text.strip(),
            'price': int(self.price_input.text.strip()),
            'availability': int(self.avail_input.text.strip()),
        }
        if self.on_save:
            self.on_save(data)
        self.dismiss()

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
        # Table header
        header = GridLayout(cols=6, size_hint_y=None, height=dp(40))
        header_cols = ['Ticket ID', 'Event', 'Tier', 'Price (₱)', 'Available', 'Actions']
        for col in header_cols:
            header_label = Label(text=col, bold=True, color=(0, 0, 0, 0.8))
            header.add_widget(header_label)
        table_card.add_widget(header)
        # Table body (scrollable)
        self.scroll = ScrollView(size_hint=(1, 1))
        self.table = GridLayout(
            cols=6,
            size_hint_y=None,
            spacing=1,
            row_force_default=True,
            row_default_height=dp(40)
        )
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
        self.table.clear_widgets()
        query = self.search_input.text.strip().lower()
        routes = get_routes()
        
        for idx, ticket in enumerate(routes):
            # Filter based on search query
            if query and not (query in ticket['ticket_id'].lower() or 
                             query in ticket['event'].lower() or 
                             query in ticket['tier'].lower()):
                continue
                
            # Row with alternating background (use very light gray)
            row_bg = (1, 1, 1, 1) if idx % 2 == 0 else ROW_ALT_GRAY
            
            # Ticket ID
            id_label = Label(text=ticket['ticket_id'], color=(0, 0, 0, 0.8))
            with id_label.canvas.before:
                Color(*row_bg)
                Rectangle(size=id_label.size, pos=id_label.pos)
            id_label.row_bg = row_bg
            id_label.bind(size=self._update_cell_bg, pos=self._update_cell_bg)
            self.table.add_widget(id_label)
            
            # Event
            event_label = Label(text=ticket['event'], color=(0, 0, 0, 0.8))
            with event_label.canvas.before:
                Color(*row_bg)
                Rectangle(size=event_label.size, pos=event_label.pos)
            event_label.row_bg = row_bg
            event_label.bind(size=self._update_cell_bg, pos=self._update_cell_bg)
            self.table.add_widget(event_label)
            
            # Tier
            tier_label = Label(text=ticket['tier'], color=(0, 0, 0, 0.8))
            with tier_label.canvas.before:
                Color(*row_bg)
                Rectangle(size=tier_label.size, pos=tier_label.pos)
            tier_label.row_bg = row_bg
            tier_label.bind(size=self._update_cell_bg, pos=self._update_cell_bg)
            self.table.add_widget(tier_label)
            
            # Price
            price_text = f"{ticket['price']:,}"
            price_label = Label(text=price_text, color=(0, 0, 0, 0.8))
            with price_label.canvas.before:
                Color(*row_bg)
                Rectangle(size=price_label.size, pos=price_label.pos)
            price_label.row_bg = row_bg
            price_label.bind(size=self._update_cell_bg, pos=self._update_cell_bg)
            self.table.add_widget(price_label)
            
            # Available
            avail_label = Label(text=str(ticket['availability']), color=(0, 0, 0, 0.8))
            with avail_label.canvas.before:
                Color(*row_bg)
                Rectangle(size=avail_label.size, pos=avail_label.pos)
            avail_label.row_bg = row_bg
            avail_label.bind(size=self._update_cell_bg, pos=self._update_cell_bg)
            self.table.add_widget(avail_label)
            
            # Actions
            actions = BoxLayout(orientation='horizontal', spacing=dp(10), padding=[dp(10), 0])
            with actions.canvas.before:
                Color(*row_bg)
                Rectangle(size=actions.size, pos=actions.pos)
            actions.row_bg = row_bg
            actions.bind(size=self._update_cell_bg, pos=self._update_cell_bg)

            # Edit button (icon)
            edit_btn = IconButton(source='icons/edit.png', size_hint=(None, None), width=dp(24), height=dp(24))
            edit_btn.bind(on_release=lambda btn, i=idx: self.open_edit_popup(i))
            actions.add_widget(edit_btn)

            # Delete button (icon)
            del_btn = IconButton(source='icons/delete.png', size_hint=(None, None), width=dp(24), height=dp(24))
            del_btn.bind(on_release=lambda btn, i=idx: self.delete_ticket(i))
            actions.add_widget(del_btn)

            # Add button (plus icon, keep as text for now)
            add_btn = Button(text='+', size_hint=(None, None), width=dp(24), height=dp(24), 
                            background_normal='', background_color=(0, 0, 0, 0))
            add_btn.bind(on_release=lambda btn, i=idx: self.increase_stock(i))
            actions.add_widget(add_btn)

            # Center the actions BoxLayout content
            actions.padding = [0, 0, 0, 0]
            actions.spacing = dp(6)
            actions.size_hint_y = 1
            actions.size_hint_x = None
            actions.width = dp(24 * 3 + 6 * 2 + 20)  # 3 icons + 2 spacings + padding
            actions.height = dp(40)
            actions.orientation = 'horizontal'
            actions.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

            self.table.add_widget(actions)
    
    def _update_cell_bg(self, instance, *args):
        instance.canvas.before.clear()
        color = getattr(instance, 'row_bg', (1, 1, 1, 1))
        with instance.canvas.before:
            Color(*color)
            Rectangle(size=instance.size, pos=instance.pos)
    
    def open_edit_popup(self, idx):
        ticket = get_routes()[idx]
        def save_callback(data):
            update_route(idx, data)
            self.refresh_table()
        TicketEditPopup(ticket=ticket, on_save=save_callback).open()
    
    def open_add_popup(self, instance):
        def save_callback(data):
            add_route(data)
            self.refresh_table()
        TicketEditPopup(ticket=None, on_save=save_callback).open()
    
    def delete_ticket(self, idx):
        remove_route(idx)
        self.refresh_table()
    
    def increase_stock(self, idx):
        ticket = get_routes()[idx]
        ticket['availability'] += 1
        update_route(idx, ticket)
        self.refresh_table()