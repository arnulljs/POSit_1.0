from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, Line
from tickets import get_routes, add_route, remove_route, update_route, get_next_ticket_id
from adminNav import NavBar

ACCENT_BLUE = (0.22, 0.27, 0.74, 1)

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
        self.route_from_input = TextInput(text=self.ticket.get('from', ''), 
                                         hint_text='From', multiline=False)
        self.route_to_input = TextInput(text=self.ticket.get('to', ''), 
                                       hint_text='To', multiline=False)
        self.class_input = TextInput(text=self.ticket.get('class', ''), 
                                    hint_text='Class', multiline=False)
        self.price_input = TextInput(text=str(self.ticket.get('price', '')), 
                                    hint_text='Price', multiline=False, 
                                    input_filter='int')
        self.avail_input = TextInput(text=str(self.ticket.get('availability', '')), 
                                    hint_text='Available', multiline=False, 
                                    input_filter='int')
        
        layout.add_widget(Label(text='Ticket ID'))
        layout.add_widget(self.ticket_id_input)
        layout.add_widget(Label(text='From'))
        layout.add_widget(self.route_from_input)
        layout.add_widget(Label(text='To'))
        layout.add_widget(self.route_to_input)
        layout.add_widget(Label(text='Class'))
        layout.add_widget(self.class_input)
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
            'from': self.route_from_input.text.strip(),
            'to': self.route_to_input.text.strip(),
            'class': self.class_input.text.strip(),
            'price': int(self.price_input.text.strip()),
            'availability': int(self.avail_input.text.strip()),
        }
        if self.on_save:
            self.on_save(data)
        self.dismiss()

class AdminInventoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set background color to white
        with self.canvas.before:
            Color(1, 1, 1, 1)  # White background
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical')
        
        # Add NavBar at the top
        self.layout.add_widget(NavBar())
        
        # Content area with padding
        content_area = BoxLayout(orientation='vertical', padding=[dp(20), dp(10)], spacing=dp(15))
        
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
            background_color=ACCENT_BLUE,
            color=(1, 1, 1, 1)
        )
        add_btn.bind(on_release=self.open_add_popup)
        action_bar.add_widget(add_btn)
        
        # Filter button (gray)
        filter_btn = Button(text='Filter', size_hint_x=None, width=dp(80), 
                           background_normal='', background_color=(0.95, 0.95, 0.95, 1), 
                           color=(0, 0, 0, 0.8))
        action_bar.add_widget(filter_btn)
        
        # Export button (gray)
        export_btn = Button(text='Export', size_hint_x=None, width=dp(80), 
                           background_normal='', background_color=(0.95, 0.95, 0.95, 1), 
                           color=(0, 0, 0, 0.8))
        action_bar.add_widget(export_btn)
        
        content_area.add_widget(action_bar)
        
        # Table container with borders
        table_container = BoxLayout(orientation='vertical')
        with table_container.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray for border
            self.table_border = Rectangle(size=table_container.size, pos=table_container.pos)
        table_container.bind(size=self._update_table_border, pos=self._update_table_border)
        
        # Table header
        header = GridLayout(cols=6, size_hint_y=None, height=dp(40))
        header_cols = ['Ticket ID', 'Route', 'Class', 'Price (₱)', 'Available', 'Actions']
        
        for col in header_cols:
            header_label = Label(text=col, bold=True, color=(0, 0, 0, 0.8))
            header.add_widget(header_label)
            
        table_container.add_widget(header)
        
        # Table body (scrollable)
        self.scroll = ScrollView(size_hint=(1, 1))
        self.table = GridLayout(
            cols=6,
            size_hint_y=None,
            spacing=1,
            row_force_default=True,
            row_default_height=dp(40)  # or whatever height you want for each row
        )
        self.table.bind(minimum_height=self.table.setter('height'))
        self.scroll.add_widget(self.table)
        table_container.add_widget(self.scroll)
        
        content_area.add_widget(table_container)
        self.layout.add_widget(content_area)
        
        self.add_widget(self.layout)
        self.refresh_table()
        self.search_input.bind(text=lambda *_: self.refresh_table())

    def _update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos
        
    def _update_table_border(self, instance, *args):
        self.table_border.size = instance.size
        self.table_border.pos = instance.pos

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
                             query in ticket['from'].lower() or 
                             query in ticket['to'].lower() or 
                             query in ticket['class'].lower()):
                continue
                
            # Row with alternating background
            row_bg = (0.98, 0.98, 0.98, 1) if idx % 2 == 0 else (1, 1, 1, 1)
            
            # Ticket ID
            id_label = Label(text=ticket['ticket_id'], color=(0, 0, 0, 0.8))
            with id_label.canvas.before:
                Color(*row_bg)
                Rectangle(size=id_label.size, pos=id_label.pos)
            id_label.row_bg = row_bg
            id_label.bind(size=self._update_cell_bg, pos=self._update_cell_bg)
            self.table.add_widget(id_label)
            
            # Route
            route_text = f"{ticket['from']}-{ticket['to']}"
            route_label = Label(text=route_text, color=(0, 0, 0, 0.8))
            with route_label.canvas.before:
                Color(*row_bg)
                Rectangle(size=route_label.size, pos=route_label.pos)
            route_label.row_bg = row_bg
            route_label.bind(size=self._update_cell_bg, pos=self._update_cell_bg)
            self.table.add_widget(route_label)
            
            # Class
            class_label = Label(text=ticket['class'], color=(0, 0, 0, 0.8))
            with class_label.canvas.before:
                Color(*row_bg)
                Rectangle(size=class_label.size, pos=class_label.pos)
            class_label.row_bg = row_bg
            class_label.bind(size=self._update_cell_bg, pos=self._update_cell_bg)
            self.table.add_widget(class_label)
            
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

            # Edit button (text placeholder)
            edit_btn = Button(text='Edit', size_hint_x=None, width=dp(60), 
                             background_normal='', background_color=(0.9, 0.9, 1, 1), color=(0,0,0,1))
            edit_btn.bind(on_release=lambda btn, i=idx: self.open_edit_popup(i))
            actions.add_widget(edit_btn)

            # Delete button (text placeholder)
            del_btn = Button(text='Delete', size_hint_x=None, width=dp(60), 
                            background_normal='', background_color=(1, 0.9, 0.9, 1), color=(0,0,0,1))
            del_btn.bind(on_release=lambda btn, i=idx: self.delete_ticket(i))
            actions.add_widget(del_btn)

            # Add button (plus icon)
            add_btn = Button(text='+', size_hint_x=None, width=dp(30), 
                            background_normal='', background_color=(0, 0, 0, 0))
            add_btn.bind(on_release=lambda btn, i=idx: self.increase_stock(i))
            actions.add_widget(add_btn)

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