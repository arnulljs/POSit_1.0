from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.metrics import dp, sp
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty, StringProperty, ObjectProperty
from kivy.animation import Animation
from kivy.uix.popup import Popup # Import Popup
from kivy.uix.textinput import TextInput # Import TextInput
from kivy.uix.widget import Widget # Import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
import xml.etree.ElementTree as ET # Import ElementTree for XML
import os # For path operations
import traceback # For detailed error logging
from datetime import date, datetime # Import date and datetime from datetime module
# from kivy.uix.spinner import Spinner # No longer needed
from adminNav import NavBar
from userNav import UserNavBar
from tickets import get_routes, get_ticket, update_ticket_availability
import auth
import re
from decimal import Decimal

# Global color definitions
normal_color = (0.22, 0.27, 0.74, 1)  # #3944BC in RGBA
pressed_color = (0.18, 0.22, 0.64, 1)  # Slightly darker shade for pressed state
gray_bg = (0.95, 0.95, 0.97, 1)  # Light gray background
white = (1, 1, 1, 1)
black = (0, 0, 0, 1)
light_button_color = (0.85, 0.85, 0.85, 1) # A lighter color for buttons

# Define tax rate
TAX_RATE = 0.12

# Define Discount Objects
discounts = [
    {'title': 'SUMMER DISCOUNT 10%', 'factor': 0.90}, # 10% discount means paying 90%
    {'title': 'SENIOR PASS DISCOUNT 20%', 'factor': 0.80}, # 20% discount means paying 80%
    {'title': 'STAFF DISCOUNT 15%', 'factor': 0.85}, # 15% discount means paying 85%
    {'title': 'No Discount', 'factor': 1.0} # Option to remove discount (paying 100%)
]

# Helper function for error popups
def display_error_popup(title, message):
    error_label = Label(text=message,
                        color=(1, 0, 0, 1),  # Bright red text
                        font_size=sp(16),
                        halign='center',
                        valign='middle')
    # Ensure text wraps within the label
    error_label.bind(size=lambda *x: setattr(error_label, 'text_size', (error_label.width - dp(20), None)))

    error_popup = Popup(title=title,
                        content=error_label,
                        size_hint=(0.6, 0.3), 
                        title_color=(1,0,0,1), 
                        title_align='center')
    error_popup.open()

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

        self.original_quantity_hint = 'Quantity'
        self.default_hint_text_color = black # Or your preferred default hint color

        # Layout for the popup content
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        # Label to show item name
        # Label to show item name, tier, and available quantity (centered, larger, new format)
        item_name_text = f"{item_data['event']}"
        tier_text = f"{item_data['tier']}"
        # item_data['stock'] will be the available quantity from RouteSelector
        # Use .get for safety, defaulting to 'N/A' if 'stock' is not present
        stock_value = item_data.get('stock', 'N/A')
        available_quantity_text = f"{stock_value} available"

        full_item_details = f"{item_name_text}\n{tier_text}\n{available_quantity_text}"

        item_label = Label(
            text=full_item_details,
            size_hint_y=None,
            height=dp(80), # Adjusted for 3 lines of larger text
            color=white,
            font_size=sp(18), # Slightly larger font size
            halign='center', # Center align text
            valign='middle'  # Middle align text vertically
        )
        item_label.bind(size=lambda *x: setattr(item_label, 'text_size', (item_label.width - dp(20), None))) # Ensure wrapping with some padding
        content.add_widget(item_label)

        # TextInput for quantity
        self.quantity_input = TextInput(
            hint_text=self.original_quantity_hint,
            input_type='number',
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            font_size=sp(16),
            padding=[dp(10), dp(10), dp(10), dp(10)], # Adjust padding
            foreground_color=black, # Color of the text user types
            hint_text_color=self.default_hint_text_color
        )
        content.add_widget(self.quantity_input)

        # Buttons for confirm and cancel
        button_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))

        confirm_button = Button(
            text='Add Item',
            background_normal="",
            background_color=(0.2, 0.7, 0.4, 1), # Kept original color for action button
            color=white # Kept original color for action button text
        )
        confirm_button.bind(on_press=self.add_item_with_quantity)

        cancel_button = Button(
            text='Cancel',
            background_normal="",
            background_color=(0.9, 0.2, 0.2, 1), # Kept original color for action button
            color=white # Kept original color for action button text
        )
        cancel_button.bind(on_press=self.dismiss)

        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)

        content.add_widget(button_layout)
        self.content = content

    def add_item_with_quantity(self, instance):
        try:
            quantity_text = self.quantity_input.text.strip()
            if not quantity_text:
                self.quantity_input.hint_text = "Quantity cannot be empty."
                self.quantity_input.hint_text_color = (1, 0, 0, 1) # Red
                self.quantity_input.text = "" # Clear input
                return

            # Use regex to ensure only positive whole numbers are accepted
            if not re.fullmatch(r"[1-9][0-9]*", quantity_text):
                self.quantity_input.hint_text = "Invalid quantity. Enter a whole number."
                self.quantity_input.hint_text_color = (1, 0, 0, 1) # Red
                self.quantity_input.text = "" # Clear input
                return

            quantity = int(quantity_text)
            available_stock = self.item_data.get('stock', 0) # Get current stock for this item

            if quantity <= 0:
                self.quantity_input.hint_text = "Quantity must be greater than 0."
                self.quantity_input.hint_text_color = (1, 0, 0, 1) # Red
                self.quantity_input.text = "" # Clear input
                return
            elif quantity > available_stock:
                self.quantity_input.hint_text = f"Only {available_stock} available. Enter less."
                self.quantity_input.hint_text_color = (1, 0, 0, 1) # Red
                self.quantity_input.text = "" # Clear input
                return

            # Reset hint text and color on successful validation
            self.quantity_input.hint_text = self.original_quantity_hint
            self.quantity_input.hint_text_color = self.default_hint_text_color
            
            # Create a copy of item_data to avoid modifying the original
            item_data_copy = self.item_data.copy()
            item_data_copy['quantity'] = quantity
            
            print(f"[DEBUG] Adding item to transaction: {item_data_copy}")
            # Call the method in TransactionPanel to add the item with quantity
            self.transaction_panel.add_item_to_transaction(item_data_copy, quantity)
            
            # Reset error state and dismiss popup
            self.quantity_input.text = ""
            self.dismiss() # Close the popup
            
        except Exception as e:
            print(f"[DEBUG] Exception in add_item_with_quantity: {e}")
            self.quantity_input.hint_text = "Invalid quantity. Enter a whole number."
            self.quantity_input.hint_text_color = (1, 0, 0, 1) # Red
            self.quantity_input.text = "" # Clear input

class PaymentMethodPopup(Popup):
    # ObjectProperty to hold the transaction panel instance
    transaction_panel = ObjectProperty(None)

    # ObjectProperty to hold the transaction panel instance
    transaction_panel = ObjectProperty(None)

    def __init__(self, transaction_panel, **kwargs):
        super(PaymentMethodPopup, self).__init__(**kwargs)
        self.transaction_panel = transaction_panel
        self.title = 'Select Payment Method'
        self.size_hint = (0.6, 0.4) # Adjust size as needed

        # Layout for the popup content
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        payment_methods = ['Cash', 'Card', 'GCash', 'Maya']
        for method in payment_methods:
            btn = Button(
                text=method,
                size_hint_y=None,
                height=dp(40),
                background_normal="",
                background_color=normal_color, # Changed to lighter color
                color=white # Changed text color to white
            )
            btn.bind(on_press=self.select_payment_method)
            content.add_widget(btn)

        self.content = content

    def select_payment_method(self, instance):
        selected_method = instance.text
        # Call a method in TransactionPanel to handle the selected payment method
        self.transaction_panel.set_payment_method(selected_method)
        self.dismiss() # Close the popup

# Discount Popup Class
class DiscountPopup(Popup):
    # ObjectProperty to hold the transaction panel instance
    transaction_panel = ObjectProperty(None)

    def __init__(self, transaction_panel, discounts_list, **kwargs):
        super(DiscountPopup, self).__init__(**kwargs)
        self.transaction_panel = transaction_panel
        self.discounts_list = discounts_list
        self.title = 'Select Discount'
        self.size_hint = (0.6, 0.5) # Adjust size as needed

        # Layout for the popup content
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        for discount in self.discounts_list:
            btn = Button(
                text=discount['title'],
                size_hint_y=None,
                height=dp(40),
                background_normal="",
                background_color=normal_color,
                color=white # Changed text color to white
            )
            # Pass the discount object to the apply_discount method
            btn.bind(on_press=lambda instance, d=discount: self.apply_discount(d))
            content.add_widget(btn)

        self.content = content

    def apply_discount(self, discount):
        # Call a method in TransactionPanel to handle the selected discount
        self.transaction_panel.set_discount(discount)
        self.dismiss() # Close the popup

# New Checkout Confirmation Popup Class
class CheckoutPopup(Popup):
    # ObjectProperty to hold the transaction panel instance
    transaction_panel = ObjectProperty(None)

    def __init__(self, transaction_panel, **kwargs):
        super(CheckoutPopup, self).__init__(**kwargs)
        self.transaction_panel = transaction_panel
        self.title = 'Confirm Purchase'
        self.size_hint = (0.8, 0.8) # Adjust size as needed

        # Layout for the popup content
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        # ScrollView for transaction details
        details_scrollview = ScrollView(size_hint=(1, 1))
        details_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        details_layout.bind(minimum_height=details_layout.setter('height'))

        # Get the current date
        today = date.today()
        date_text = today.strftime("%B %d, %Y") # Format the date

        # Add transaction details including date and ID
        details_layout.add_widget(Label(text=f"Transaction ID: {self.transaction_panel.transaction_id_text}", size_hint_y=None, height=dp(30), halign='left', color=white, bold=True)) # Changed text color to white
        details_layout.add_widget(Label(text=f"Date: {date_text}", size_hint_y=None, height=dp(30), halign='left', color=white, bold=True)) # Added Date
        details_layout.add_widget(Label(text="Items:", size_hint_y=None, height=dp(25), halign='left', color=white, bold=True)) # Changed text color to white

        # Add items list
        for item in self.transaction_panel.transaction_items:
            item_details = f"- {item['event']} ({item['tier']}) x{item['quantity']} @ ₱{item['price']:.2f} each"
            details_layout.add_widget(Label(text=item_details, size_hint_y=None, height=dp(20), halign='left', color=white)) # Changed text color to white

        details_layout.add_widget(Label(text="", size_hint_y=None, height=dp(10))) # Spacer

        # Add summary details
        details_layout.add_widget(Label(text=f"Subtotal: ₱{self.transaction_panel.subtotal:.2f}", size_hint_y=None, height=dp(25), halign='left', color=white)) # Changed text color to white
        details_layout.add_widget(Label(text=f"Tax ({TAX_RATE*100:.0f}%): ₱{self.transaction_panel.tax:.2f}", size_hint_y=None, height=dp(25), halign='left', color=white)) # Changed text color to white

        # Add Discount Title and Amount
        details_layout.add_widget(Label(text=f"Discount Applied: {self.transaction_panel.selected_discount['title']}", size_hint_y=None, height=dp(25), halign='left', color=white)) # Added Discount Title
        details_layout.add_widget(Label(text=f"Discount Amount: -₱{self.transaction_panel.discount_amount:.2f}", size_hint_y=None, height=dp(25), halign='left', color=white)) # Changed text color to white

        details_layout.add_widget(Label(text=f"TOTAL: ₱{self.transaction_panel.total:.2f}", size_hint_y=None, height=dp(30), halign='left', color=white, bold=True)) # Changed text color to white
        details_layout.add_widget(Label(text=f"Payment Method: {self.transaction_panel.selected_payment_method}", size_hint_y=None, height=dp(25), halign='left', color=white)) # Changed text color to white
        
        # Robust cash tendered display
        try:
            cash_tendered_display_float = float(self.transaction_panel.cash_tendered)
            cash_tendered_display_text = f"₱{cash_tendered_display_float:.2f}"
        except ValueError:
            cash_tendered_display_text = "Invalid Cash Amount"
        details_layout.add_widget(Label(text=f"Cash Tendered: {cash_tendered_display_text}", size_hint_y=None, height=dp(25), halign='left', color=white))

        # Calculate and display change
        try:
            cash_tendered_float = float(self.transaction_panel.cash_tendered)
            change = cash_tendered_float - self.transaction_panel.total
            change_text = f"Change: ₱{change:.2f}" if change >= 0 else "Change: Insufficient Cash"
        except ValueError:
            change_text = "Change: Invalid Cash Amount"
        details_layout.add_widget(Label(text=change_text, size_hint_y=None, height=dp(30), halign='left', color=white, bold=True))

        # Add a placeholder for a confirmation message
        details_layout.add_widget(Label(text="", size_hint_y=None, height=dp(20))) # Spacer
        details_layout.add_widget(Label(text="Thank you for your purchase!", size_hint_y=None, height=dp(30), halign='center', color=white, bold=True)) # Added confirmation message

        details_scrollview.add_widget(details_layout)
        content.add_widget(details_scrollview)

        # Buttons for confirm and cancel
        button_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))

        confirm_button = Button(
            text='Confirm Purchase',
            background_normal="",
            background_color=(0.2, 0.7, 0.4, 1), # Kept original color for action button
            color=white # Kept original color for action button text
        )
        confirm_button.bind(on_press=self.confirm_purchase)

        cancel_button = Button(
            text='Cancel',
            background_normal="",
            background_color=(0.9, 0.2, 0.2, 1), # Kept original color for action button
            color=white # Kept original color for action button text
        )
        cancel_button.bind(on_press=self.dismiss)

        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)

        content.add_widget(button_layout)
        self.content = content

    def confirm_purchase(self, instance):
        print("Confirm Purchase button pressed.")
        current_transaction_id = self.transaction_panel.transaction_id_text
        print(f"Attempting to confirm and save purchase for Transaction ID: {current_transaction_id}")

        # Save transaction to XML and get status
        print(f"Saving transaction data for {current_transaction_id} to XML...")
        save_success, save_message_or_filename = self.save_transaction_to_xml()

        if save_success:
            print(f"Successfully saved XML for {current_transaction_id} to {save_message_or_filename}")

            # Save transaction to database
            print(f"Saving transaction data for {current_transaction_id} to database...")
            db_save_success, db_save_message = self.save_transaction_to_db()
            
            if not db_save_success:
                print(f"Warning: Failed to save transaction to database: {db_save_message}")
                # Continue with the transaction even if DB save fails
                # We still have the XML backup

            # ---- DECREMENT STOCK ----
            try:
                all_current_tickets = get_routes() # Get fresh list of all tickets
                items_purchased_details = self.transaction_panel.transaction_items

                for purchased_item_info in items_purchased_details:
                    event_name = purchased_item_info['event']
                    tier_name = purchased_item_info['tier']
                    quantity_bought = purchased_item_info['quantity']

                    # Find the ticket in all_current_tickets and its index
                    ticket_index_to_update = -1
                    ticket_data_to_update = None

                    for i, ticket_in_stock in enumerate(all_current_tickets):
                        # Assuming event and tier uniquely identify a ticket type
                        if ticket_in_stock['event'] == event_name and \
                           ticket_in_stock['tier'] == tier_name:
                            ticket_index_to_update = i
                            ticket_data_to_update = ticket_in_stock.copy() # Work on a copy
                            break
                    
                    if ticket_data_to_update and ticket_index_to_update != -1:
                        new_availability = ticket_data_to_update.get('availability', 0) - quantity_bought
                        ticket_data_to_update['availability'] = max(0, new_availability) # Ensure not negative
                        
                        update_ticket_availability(ticket_index_to_update, ticket_data_to_update)
                        print(f"Stock updated for {event_name} ({tier_name}): new availability {ticket_data_to_update['availability']}")
                    else:
                        print(f"WARNING: Could not find ticket {event_name} ({tier_name}) in stock to update availability.")
            except Exception as e:
                print(f"ERROR updating stock availability: {e}")
                traceback.print_exc() # For more details
            # ---- END DECREMENT STOCK ----
        else:
            print(f"ERROR: Failed to save XML for {current_transaction_id}. Reason: {save_message_or_filename}")
            # Show an error popup to the user
            error_label = Label(text=f"XML Save Failed:\n{save_message_or_filename}",
                                color=(1, 0, 0, 1),  # Bright red text
                                font_size=sp(16),
                                halign='center',
                                valign='middle')
            # Ensure text wraps within the label
            error_label.bind(size=lambda *x: setattr(error_label, 'text_size', (error_label.width - dp(20), None)))

            error_popup = Popup(title='XML Save Error',
                                content=error_label,
                                size_hint=(0.7, 0.5), # Make it a good portion of the screen
                                title_color=(1,0,0,1), # Red title for popup
                                title_align='center')
            error_popup.open()

        print(f"Purchase processing complete for Transaction ID: {current_transaction_id}.")

        # Increment the transaction ID for the *next* transaction
        self.transaction_panel.generate_transaction_id()
        print(f"New transaction ID generated: {self.transaction_panel.transaction_id_text}")

        # Clear the current transaction from the panel
        self.transaction_panel.cancel_transaction(None) # Use the existing cancel logic to clear

        # Refresh the RouteSelector display in MainScreen
        try:
            # self.transaction_panel.parent is content_layout
            # self.transaction_panel.parent.parent is MainScreen instance
            # Corrected path: transaction_panel.parent (content_layout) -> .parent (root_layout) -> .parent (MainScreen)
            main_screen_instance = self.transaction_panel.parent.parent.parent

            if hasattr(main_screen_instance, 'route_selector') and \
               hasattr(main_screen_instance.route_selector, 'filter_routes'):
                print("Refreshing RouteSelector after purchase...")
                main_screen_instance.route_selector.filter_routes()
            else:
                print(f"WARNING: Could not find route_selector on MainScreen instance ({main_screen_instance}) to refresh.")
                # Fallback attempt if direct parent traversal fails or structure changes
                app = App.get_running_app()
                if app and app.root and hasattr(app.root, 'current_screen'):
                    current_screen_widget = app.root.current_screen
                    if isinstance(current_screen_widget, MainScreen): # Ensure it's the MainScreen
                        if hasattr(current_screen_widget, 'route_selector') and \
                           hasattr(current_screen_widget.route_selector, 'filter_routes'):
                            print("Refreshing RouteSelector via App.get_running_app()...")
                            current_screen_widget.route_selector.filter_routes()
                        else:
                            print("Found MainScreen via App, but its route_selector is missing or filter_routes method.")
                    else:
                        print(f"Current screen '{current_screen_widget.name if current_screen_widget else 'None'}' is not the expected MainScreen.")
        except Exception as e:
            print(f"Error refreshing RouteSelector: {e}")
            traceback.print_exc()
        self.dismiss() # Close the popup

    def save_transaction_to_xml(self):
        """Saves the current transaction details to an XML file."""
        try:
            tp = self.transaction_panel
            if not tp.transaction_id_text:
                return False, "Transaction ID is empty. Cannot save XML."

            # Create an Element for the current transaction
            transaction_element = ET.Element("Transaction")
            
            # Use a dictionary to store all elements for faster access
            elements = {
                'TransactionID': tp.transaction_id_text,
                'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add basic transaction info
            for key, value in elements.items():
                ET.SubElement(transaction_element, key).text = str(value)

            # Add items in a single loop
            items_xml = ET.SubElement(transaction_element, "Items")
            for item in tp.transaction_items:
                item_xml = ET.SubElement(items_xml, "Item")
                item_data = {
                    'Event': item['event'],
                    'Tier': item['tier'],
                    'Quantity': str(item['quantity']),
                    'PricePerItem': f"{item['price']:.2f}",
                    'ItemTotal': f"{item['price'] * item['quantity']:.2f}"
                }
                for key, value in item_data.items():
                    ET.SubElement(item_xml, key).text = str(value)

            # Add summary in a single block
            summary_xml = ET.SubElement(transaction_element, "Summary")
            summary_data = {
                'Subtotal': f"{tp.subtotal:.2f}",
                'TaxRate': f"{TAX_RATE*100:.0f}%",
                'TaxAmount': f"{tp.tax:.2f}",
                'DiscountTitle': tp.selected_discount['title'],
                'DiscountFactor': str(tp.selected_discount['factor']),
                'DiscountAmount': f"{tp.discount_amount:.2f}",
                'Total': f"{tp.total:.2f}"
            }
            for key, value in summary_data.items():
                ET.SubElement(summary_xml, key).text = str(value)

            # Add payment info
            payment_xml = ET.SubElement(transaction_element, "Payment")
            payment_data = {
                'PaymentMethod': tp.selected_payment_method,
                'CashTendered': f"{float(tp.cash_tendered):.2f}",
                'Change': f"{float(tp.cash_tendered) - tp.total:.2f}"
            }
            for key, value in payment_data.items():
                ET.SubElement(payment_xml, key).text = str(value)

            # --- Logic for daily XML file ---
            today_str = date.today().strftime("%Y-%m-%d")
            transactions_dir = "transactions"
            if not os.path.exists(transactions_dir):
                os.makedirs(transactions_dir)
            daily_filename = os.path.join(transactions_dir, f"transactions_{today_str}.xml")

            # Create or load the daily transactions file
            try:
                if os.path.exists(daily_filename):
                    tree = ET.parse(daily_filename)
                    daily_root = tree.getroot()
                    if daily_root.tag != "DailyTransactions":
                        daily_root = ET.Element("DailyTransactions")
                        tree = ET.ElementTree(daily_root)
                else:
                    daily_root = ET.Element("DailyTransactions")
                    tree = ET.ElementTree(daily_root)
            except ET.ParseError:
                daily_root = ET.Element("DailyTransactions")
                tree = ET.ElementTree(daily_root)

            # Add the transaction and save
            daily_root.append(transaction_element)
            ET.indent(tree, space="\t", level=0)
            tree.write(daily_filename, encoding="utf-8", xml_declaration=True)

            return True, daily_filename

        except Exception as e:
            error_details = traceback.format_exc()
            print(f"[XML SAVE] CRITICAL ERROR saving transaction to XML: {e}\n{error_details}")
            return False, f"XML generation/write error: {str(e)}\nSee console for details."

    def save_transaction_to_db(self):
        """Saves the current transaction details to the database."""
        try:
            tp = self.transaction_panel
            if not tp.transaction_id_text:
                return False, "Transaction ID is empty. Cannot save to database."

            # Get the current user's ID from the session
            from auth import session
            user_id = None
            if session["username"]:
                from db_config import execute_query
                query = "SELECT id FROM users WHERE username = %s"
                result = execute_query(query, (session["username"],), fetch=True)
                if result:
                    user_id = result[0]['id']

            # Get all ticket IDs in one query to avoid multiple database calls
            ticket_ids = {}
            ticket_query = "SELECT ticket_id, event, tier FROM tickets"
            ticket_results = execute_query(ticket_query, fetch=True)
            for ticket in ticket_results:
                key = (ticket['event'], ticket['tier'])
                ticket_ids[key] = ticket['ticket_id']

            # Prepare all transaction items for batch insert
            item_values = []
            for item in tp.transaction_items:
                key = (item['event'], item['tier'])
                if key not in ticket_ids:
                    return False, f"Ticket not found in database: {item['event']} - {item['tier']}"
                
                ticket_id = ticket_ids[key]
                item_values.append((
                    ticket_id,
                    item['quantity'],
                    float(item['price'])
                ))

            # Insert transaction and items in a single transaction
            from db_config import execute_query
            transaction_query = """
                INSERT INTO transactions 
                (transaction_id, user_id, total_amount, tax_amount, discount_amount, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            transaction_params = (
                tp.transaction_id_text,
                user_id,
                float(tp.total),
                float(tp.tax),
                float(tp.discount_amount)
            )
            
            # Execute transaction insert and get ID
            execute_query(transaction_query, transaction_params)
            get_trans_id_query = "SELECT id FROM transactions WHERE transaction_id = %s"
            trans_result = execute_query(get_trans_id_query, (tp.transaction_id_text,), fetch=True)
            
            if not trans_result:
                return False, "Failed to retrieve inserted transaction ID"
            
            transaction_db_id = trans_result[0]['id']

            # Insert transaction items one by one
            if item_values:
                item_query = """
                    INSERT INTO transaction_items 
                    (transaction_id, ticket_id, quantity, price_at_sale, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                """
                for item in item_values:
                    execute_query(item_query, (transaction_db_id,) + item)

            return True, "Transaction saved to database successfully"

        except Exception as e:
            error_details = traceback.format_exc()
            print(f"[DB SAVE] CRITICAL ERROR saving transaction to database: {e}\n{error_details}")
            return False, f"Database error: {str(e)}\nSee console for details."

class RouteSelector(BoxLayout):
    def __init__(self, transaction_panel, **kwargs):
        print('RouteSelector __init__')
        super(RouteSelector, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(15)
        self.size_hint_y = 1
        self.transaction_panel = transaction_panel # Store the transaction panel instance
        self.selected_card_key = None  # Track selected card (event, tier)

        # Add a white background with rounded corners
        with self.canvas.before:
            Color(*white)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(5)])
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Placeholders for filter button references
        self.tier_filter_buttons = []
        self.artist_filter_buttons = []
        self.filter_layout = None
        self.selected_tier = 'All Tiers'
        self.selected_artist = 'All Artists'

        # Build filter tabs and add as first widget
        self.build_filter_tabs()

        # Add route cards in a scrollview (always after filter bars)
        self.route_container = GridLayout(cols=2, spacing=dp(15), size_hint_y=None)
        self.route_container.bind(minimum_height=self.route_container.setter('height'))

        self.scrollview = ScrollView(size_hint=(1, 1))
        self.scrollview.add_widget(self.route_container)
        self.add_widget(self.scrollview)

        # Load routes
        self.filter_routes()

    def build_filter_tabs(self):
        # Remove old filter layout if it exists
        if self.filter_layout and self.filter_layout in self.children:
            self.remove_widget(self.filter_layout)
        self.tier_filter_buttons = []
        self.artist_filter_buttons = []

        # Get unique tiers and artists from current routes
        routes = get_routes()
        tiers = sorted(set(route['tier'] for route in routes))
        artists = sorted(set(route['event'] for route in routes))
        tiers = ['All Tiers'] + tiers
        artists = ['All Artists'] + artists

        # Create main filter layout with horizontal padding
        filter_layout = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(120), spacing=dp(5), padding=[dp(10), 0, dp(10), 0])
        self.filter_layout = filter_layout

        # Tier filter tabs
        tier_layout = BoxLayout(size_hint=(1, None), height=dp(40), spacing=dp(5), padding=[0, 0, 0, 0])
        tier_label = Label(
            text="Filter by Tier:",
            size_hint=(None, 1),
            width=dp(90),
            color=black,
            halign='left',
            valign='middle'
        )
        tier_layout.add_widget(tier_label)
        for tier in tiers:
            btn = ToggleButton(
                text=tier,
                group="tier_tabs",
                size_hint=(1, 1),
                font_size=sp(14),
                background_normal="",
                background_down="",
                background_color=(0,0,0,0),
                color=black,
                bold=False,
                padding=[dp(8), 0]
            )
            if tier == self.selected_tier:
                btn.state = "down"
                with btn.canvas.before:
                    Color(*normal_color)
                    RoundedRectangle(size=btn.size, pos=btn.pos, radius=[dp(5)])
            else:
                with btn.canvas.before:
                    Color(0.9, 0.9, 0.9, 1)
                    RoundedRectangle(size=btn.size, pos=btn.pos, radius=[dp(5)])
            btn.bind(size=self._update_tab_bg, pos=self._update_tab_bg, state=self._update_tab_state)
            btn.bind(on_press=lambda x, t=tier: self.set_tier_filter(t))
            tier_layout.add_widget(btn)
            self.tier_filter_buttons.append(btn)

        # Artist filter tabs (scrollable)
        artist_scroll = ScrollView(size_hint=(1, None), height=dp(40), do_scroll_x=True, do_scroll_y=False, bar_width=dp(6))
        artist_layout = BoxLayout(size_hint=(None, 1), height=dp(40), spacing=dp(5), padding=[0, 0, 0, 0])
        artist_layout.bind(minimum_width=artist_layout.setter('width'))
        artist_label = Label(
            text="Filter by Artist:",
            size_hint=(None, 1),
            width=dp(90),
            color=black,
            halign='left',
            valign='middle'
        )
        artist_layout.add_widget(artist_label)
        for artist in artists:
            btn = ToggleButton(
                text=artist,
                group="artist_tabs",
                size_hint=(None, 1),
                width=dp(140),
                font_size=sp(14),
                background_normal="",
                background_down="",
                background_color=(0,0,0,0),
                color=black,
                bold=False,
                padding=[dp(8), 0]
            )
            if artist == self.selected_artist:
                btn.state = "down"
                with btn.canvas.before:
                    Color(*normal_color)
                    RoundedRectangle(size=btn.size, pos=btn.pos, radius=[dp(5)])
            else:
                with btn.canvas.before:
                    Color(0.9, 0.9, 0.9, 1)
                    RoundedRectangle(size=btn.size, pos=btn.pos, radius=[dp(5)])
            btn.bind(size=self._update_tab_bg, pos=self._update_tab_bg, state=self._update_tab_state)
            btn.bind(on_press=lambda x, a=artist: self.set_artist_filter(a))
            artist_layout.add_widget(btn)
            self.artist_filter_buttons.append(btn)
        artist_scroll.add_widget(artist_layout)

        # Add refresh button to the right
        refresh_layout = BoxLayout(size_hint=(1, None), height=dp(40), spacing=dp(5), padding=[0, 0, 0, 0])
        refresh_layout.add_widget(Widget(size_hint_x=0.7))  # Spacer
        refresh_btn = Button(
            text="Refresh Items",
            size_hint=(None, 1),
            width=dp(140),
            background_color=(0.22, 0.27, 0.74, 1),
            color=(1, 1, 1, 1),
            font_size=sp(14),
            background_normal='',
            border=(16, 16, 16, 16)
        )
        refresh_btn.bind(on_release=lambda instance: self.load_routes(get_routes()))
        refresh_layout.add_widget(refresh_btn)

        # Add all layouts to the main filter layout
        filter_layout.add_widget(tier_layout)
        filter_layout.add_widget(artist_scroll)
        filter_layout.add_widget(refresh_layout)

        # Always add filter bars as the first widget (at the top)
        self.add_widget(filter_layout, index=0)

    def _update_rect(self, instance, value):
        instance.rect.size = instance.size
        instance.rect.pos = instance.pos

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

    def set_tier_filter(self, tier):
        self.selected_tier = tier
        for btn in self.tier_filter_buttons:
            btn.state = 'down' if btn.text == tier else 'normal'
            self._update_tab_bg(btn, btn.size)
            self._update_tab_state(btn, btn.state)
        self.filter_routes()

    def set_artist_filter(self, artist):
        self.selected_artist = artist
        for btn in self.artist_filter_buttons:
            btn.state = 'down' if btn.text == artist else 'normal'
            self._update_tab_bg(btn, btn.size)
            self._update_tab_state(btn, btn.state)
        self.filter_routes()

    def filter_routes(self):
        routes = get_routes()
        filtered = []
        for route in routes:
            if (self.selected_tier == 'All Tiers' or route['tier'] == self.selected_tier) and \
               (self.selected_artist == 'All Artists' or route['event'] == self.selected_artist):
                filtered.append(route)
        self.load_routes(filtered)

    def load_routes(self, routes):
        self.route_container.clear_widgets()
        for ticket in routes:
            card = self.create_route_card(
                ticket["event"],
                ticket["tier"],
                ticket["price"],
                ticket["availability"]  # Assuming this is the stock quantity
            )
            self.route_container.add_widget(card)

    def create_route_card(self, event, tier, price, stock_quantity):
        card = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(140),
            padding=dp(10)
        )

        is_available_for_purchase = stock_quantity > 0

        # Create border based on tier and store original color
        border_color = (0.85, 0.7, 0.1, 1) if tier == "Gold Seating" else ((0.75, 0.75, 0.75, 1) if tier == "Silver Seating" else (0.4, 0.4, 0.4, 1))
        card.original_border_color = border_color # Store original color

        with card.canvas.before:
            # Always use white background
            Color(*white)
            self.card_rect = RoundedRectangle(size=card.size, pos=card.pos, radius=[dp(8)])

            # Add border with tier color
            Color(*border_color, group='color_border')
            card.border_instruction = RoundedRectangle(
                size=card.size, pos=card.pos, radius=[dp(8)],
                line_width=dp(1.5) if is_available_for_purchase else dp(0),
                width=dp(1.5) if is_available_for_purchase else dp(0)
            )

        card.bind(size=lambda obj, val: self._update_card_rect(obj, val, obj.original_border_color, is_available_for_purchase),
                  pos=lambda obj, val: self._update_card_rect(obj, val, obj.original_border_color, is_available_for_purchase))

        # Always show artist, tier, and price on their own lines
        event_label = Label(
            text=f"{event}",
            font_size=sp(16),
            bold=True,
            color=black,
            size_hint=(1, None),
            height=dp(28),
            halign='left',
            valign='middle'
        )
        event_label.bind(size=self._update_label)
        tier_label = Label(
            text=f"{tier}",
            font_size=sp(13),
            color=black,
            size_hint=(1, None),
            height=dp(20),
            halign='left',
            valign='middle'
        )
        tier_label.bind(size=self._update_label)
        price_label = Label(
            text=f"₱{price:,}",
            font_size=sp(18),
            bold=True,
            color=black if is_available_for_purchase else (0.6, 0.6, 0.6, 1),
            size_hint=(1, None),
            height=dp(25),
            halign='left',
            valign='middle'
        )
        price_label.bind(size=self._update_label)
        card.add_widget(event_label)
        card.add_widget(tier_label)
        card.add_widget(price_label)

        # For unavailable card, show "OUT OF STOCK"
        # Add stock level indicators (Low Stock, Critically Low Stock) if applicable
        stock_indicator_label = None
        if 1 <= stock_quantity <= 5:
            stock_indicator_label = Label(
                text="CRITICALLY LOW STOCK",
                font_size=sp(12),
                bold=True,
                color=(1, 0, 0, 1), # Red color for critically low
                size_hint=(1, None),
                height=dp(20),
                halign='left',
                valign='middle'
            )
        elif 6 <= stock_quantity <= 10:
            stock_indicator_label = Label(
                text="LOW STOCK",
                font_size=sp(12),
                bold=True,
                color=(1, 0, 0, 1), # Red color for low
                size_hint=(1, None),
                height=dp(20),
                halign='left',
                valign='middle'
            )

        if not is_available_for_purchase:
            card.opacity = 0.7
            out_label = Label(
                text="OUT OF STOCK",
                font_size=sp(14),
                bold=True,
                color=(0.8, 0, 0, 1),
                size_hint=(1, None),
                height=dp(20),
                halign='center',
                valign='middle'
            )
            card.add_widget(out_label)
        else: # Item is available for purchase (stock > 0)
            # Make card selectable
            card.bind(on_touch_down=lambda obj, touch: self.select_card(obj, touch, {"event": event, "tier": tier, "price": price, "stock": stock_quantity}))
            if stock_indicator_label: # If low or critically low stock, add the indicator
                stock_indicator_label.bind(size=self._update_label)
                card.add_widget(stock_indicator_label)

        return card

    def _update_label(self, instance, value):
        instance.text_size = (instance.width, None)

    def _update_card_rect(self, instance, value, border_color, is_available_for_purchase):
        instance.canvas.before.clear()
        with instance.canvas.before:
            # Always use white background
            Color(*white)
            RoundedRectangle(size=instance.size, pos=instance.pos, radius=[dp(8)])

            # Add border with tier color, only if available for purchase
            Color(*border_color, group='color_border')
            instance.border_instruction = RoundedRectangle(
                size=instance.size, pos=instance.pos, radius=[dp(8)],
                line_width=dp(1.5) if is_available_for_purchase else dp(0),
                width=dp(1.5) if is_available_for_purchase else dp(0)
            )

    def select_card(self, instance, touch, item_data):
        if instance.collide_point(*touch.pos):
            # Set this card as selected and refresh the route cards
            self.selected_card_key = (item_data['event'], item_data['tier'])
            self.filter_routes()  # This will redraw the cards with the new selection
            # Trigger the pulse animation
            self.animate_card_pulse(instance, instance.original_border_color)
            # Delay opening the quantity popup so the UI can update
            Clock.schedule_once(lambda dt: self._open_quantity_popup(item_data), 0.1)
            return True
        return False # Return False if touch is not within the card

    def _open_quantity_popup(self, item_data):
        popup = QuantityPopup(transaction_panel=self.transaction_panel, item_data=item_data)
        popup.open()

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
    selected_payment_method = StringProperty("Payment Method") # Property to hold selected payment method
    cash_tendered = StringProperty("0.00") # Property to hold cash tendered amount
    selected_discount = ObjectProperty(discounts[-1]) # Property to hold the selected discount, default to 'No Discount'
    discount_amount = NumericProperty(0) # Property to hold the calculated discount amount
    transaction_id_text = StringProperty("") # Property to hold the formatted transaction ID

    # Class variable to keep track of the transaction counter
    _transaction_counter = 0

    def __init__(self, **kwargs):
        print('TransactionPanel __init__')
        super(TransactionPanel, self).__init__(**kwargs)
        self.orientation = 'vertical'
        # Decreased overall spacing for the TransactionPanel
        self.spacing = dp(5)
        self.padding = dp(15)
        # self.size_hint_x = 0.25 # Removed size_hint_x here, set in MainScreen

        # --- Initialize transaction counter by finding the max ID from today's XML file ---
        today_str = date.today().strftime("%Y-%m-%d")
        transactions_dir = "transactions"
        daily_root_tag = "DailyTransactions"
        max_existing_id = 0

        # Ensure the transactions directory exists
        if not os.path.exists(transactions_dir):
            try:
                os.makedirs(transactions_dir)
                print(f"[INIT] Created directory: {transactions_dir}")
            except OSError as e:
                print(f"[INIT] CRITICAL: Error creating directory {transactions_dir}: {e}. Transaction saving might fail.")
                # Depending on desired behavior, you might want to raise an error or display a popup

        daily_filename = os.path.join(transactions_dir, f"transactions_{today_str}.xml")

        if os.path.exists(daily_filename):
            try:
                tree = ET.parse(daily_filename)
                daily_root = tree.getroot()
                if daily_root.tag == daily_root_tag:
                    for transaction_element in daily_root.findall("Transaction"):
                        id_element = transaction_element.find("TransactionID")
                        if id_element is not None and id_element.text:
                            try:
                                current_id = int(id_element.text)
                                if current_id > max_existing_id:
                                    max_existing_id = current_id
                            except ValueError:
                                print(f"[INIT] Warning: Non-integer TransactionID '{id_element.text}' found in {daily_filename}. Skipping.")
                    print(f"[INIT] Max existing TransactionID for {today_str} is {max_existing_id} from {daily_filename}.")
                else:
                    print(f"[INIT] Warning: File {daily_filename} has unexpected root tag '{daily_root.tag}'. Max ID not determined from this file.")
            except ET.ParseError:
                print(f"[INIT] Warning: Could not parse {daily_filename}. Max ID not determined from this file.")
            except Exception as e:
                print(f"[INIT] Error reading {daily_filename} to determine max transaction ID: {e}")
        
        TransactionPanel._transaction_counter = max_existing_id # Initialize with the highest ID found
        # --- End of transaction counter initialization ---

        # Add a white background
        with self.canvas.before:
            Color(*white)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Transaction header and ID in the same row
        header_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(30))

        header = Label(
            text="Current Transaction",
            font_size=sp(16),
            bold=True,
            size_hint=(0.7, 1), # Adjust size hint to give space for ID
            halign='left',
            color=black
        )
        header.bind(size=self._update_label)

        # Label to display the dynamic transaction ID
        self.transaction_id_label = Label(
            text=self.transaction_id_text, # Bind to the property
            font_size=sp(14),
            size_hint=(0.3, 1), # Adjust size hint for ID
            halign='right',
            color=(0.5, 0.5, 0.5, 1)
        )
        self.transaction_id_label.bind(size=self._update_label)
        # Bind the label's text to the transaction_id_text property
        self.bind(transaction_id_text=self.update_transaction_id_label)


        header_layout.add_widget(header)
        header_layout.add_widget(self.transaction_id_label) # Use the label instance

        self.add_widget(header_layout) # Add the new horizontal layout

        # Generate the initial transaction ID
        self.generate_transaction_id()


        # Container for dynamically added items
        self.items_container = BoxLayout(orientation='vertical', size_hint=(1, None), spacing=dp(10))
        # Bind height to children's minimum_height to allow scrolling if needed
        self.items_container.bind(minimum_height=self.items_container.setter('height'))

        # Add a ScrollView for the items_container
        items_scrollview = ScrollView(size_hint=(1, 1))
        items_scrollview.add_widget(self.items_container)
        self.add_widget(items_scrollview)

        # Removed the flexible space widget here
        # self.add_widget(BoxLayout(size_hint_y=1)) # Flexible space

        # Subtotal, Tax, Discount, and TOTAL text and amounts (moved here, below payment methods)
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

        # Discount display
        discount_layout = BoxLayout(size_hint=(1, None), height=dp(25)) # Adjusted height
        discount_label = Label(
            text="Discount",
            font_size=sp(14),
            size_hint=(0.5, 1),
            halign='left',
            color=black
        )
        discount_label.bind(size=self._update_label)

        self.discount_amount_label = Label( # Use a property for this label
            text=f"-₱{self.discount_amount:,.2f}",
            font_size=sp(14),
            size_hint=(0.5, 1),
            halign='right',
            color=black
        )
        self.discount_amount_label.bind(size=self._update_label)

        discount_layout.add_widget(discount_label)
        discount_layout.add_widget(self.discount_amount_label) # Add the discount amount label
        self.add_widget(discount_layout)

        self.line = BoxLayout(size_hint=(1, None), height=dp(1))
        with self.line.canvas:
            Color(0.8, 0.8, 0.8, 1)
            Rectangle(size=self.line.size, pos=self.line.pos)
        self.line.bind(size=self._update_line, pos=self._update_line)
        self.add_widget(self.line)

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


        # Payment Method Button to open popup
        self.payment_method_button = Button(
            text=self.selected_payment_method, # Use the property for text
            size_hint=(1, None),
            height=dp(40),
            background_normal="",
            background_color=normal_color,
            color=white,
            font_size=sp(16)
        )
        self.payment_method_button.bind(on_press=self.show_payment_method_popup)
        self.add_widget(self.payment_method_button)

        # Bind the button's text to the selected_payment_method property
        self.bind(selected_payment_method=self.update_payment_method_button_text)

        # Cash Tendered Display (similar to Total)
        cash_layout = BoxLayout(size_hint=(1, None), height=dp(35)) # Adjusted height
        cash_label = Label(
            text="CASH",
            font_size=sp(16),
            bold=True,
            size_hint=(0.5, 1),
            halign='left',
            color=black
        )
        cash_label.bind(size=self._update_label)

        self.cash_amount_label = Label(
            text=f"₱{float(self.cash_tendered):,.2f}", # Format as currency
            font_size=sp(16),
            bold=True,
            size_hint=(0.5, 1),
            halign='right',
            color=black
        )
        self.cash_amount_label.bind(size=self._update_label)

        cash_layout.add_widget(cash_label)
        cash_layout.add_widget(self.cash_amount_label)
        self.add_widget(cash_layout)

        # Bind cash_amount_label text to cash_tendered property
        self.bind(cash_tendered=self.update_cash_display)


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
            # Bind numpad buttons to process_numpad_input method
            btn.bind(on_press=lambda instance, val=btn_text: self.process_numpad_input(val))
            numpad_layout.add_widget(btn)

        self.add_widget(numpad_layout)

        # Bottom action buttons (Cancel, Discount, Checkout)
        bottom_actions = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(120), spacing=dp(10))

        cancel_discount_layout = BoxLayout(size_hint=(1, None), height=dp(40), spacing=dp(10))
        cancel_btn = Button(
            text="Cancel",
            size_hint=(0.5, None),
            height=dp(40),
            background_normal="",
            background_color=(0.9, 0.2, 0.2, 1),
            color=white
        )
        # Bind the cancel button to the new cancel_transaction method
        cancel_btn.bind(on_press=self.cancel_transaction)

        self.discount_btn = Button( # Store discount_btn as a property
            text="Discount",
            size_hint=(0.5, None),
            height=dp(40),
            background_normal="",
            background_color=(1, 0.6, 0, 1),
            color=white
        )
        # Bind the discount button to show the discount popup
        self.discount_btn.bind(on_press=self.show_discount_popup)
        cancel_discount_layout.add_widget(cancel_btn)
        cancel_discount_layout.add_widget(self.discount_btn) # Use self.discount_btn


        self.checkout_btn = Button(
            text=f"Checkout ₱{self.total:,.2f}",
            size_hint=(1, None),
            height=dp(50),
            background_normal="",
            background_color=(0.2, 0.7, 0.4, 1),
            color=white,
            font_size=sp(16)
        )
        # Bind the checkout button to show the checkout popup
        self.checkout_btn.bind(on_press=self.show_checkout_popup)


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
            Rectangle(size=self.line.size, pos=self.line.pos)

    def _update_label(self, instance, value):
        instance.text_size = (instance.width, None)

    # New method to generate and format the transaction ID
    def generate_transaction_id(self):
        TransactionPanel._transaction_counter += 1
        self.transaction_id_text = f"{TransactionPanel._transaction_counter:05d}" # Format as 5 digits with leading zeros

    # Method to update the transaction ID label text
    def update_transaction_id_label(self, instance, value):
        self.transaction_id_label.text = f"#{value}" # Add '#' prefix

    # Method to add an item to the transaction with a specified quantity
    def add_item_to_transaction(self, item_data, quantity):
        # Convert Decimal price to float
        if isinstance(item_data['price'], Decimal):
            item_data['price'] = float(item_data['price'])
            
        # Check if the item is already in the list
        found = False
        for item in self.transaction_items:
            if item['event'] == item_data['event'] and item['tier'] == item_data['tier']:
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
        self.calculate_totals() # Recalculate totals after adding/updating item
        self.update_total_display()

    # Method to update the display of items in the transaction panel
    def update_items_display(self):
        self.items_container.clear_widgets()
        for item in self.transaction_items:
            item_widget = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(70))

            item_header = BoxLayout(size_hint=(1, None), height=dp(25))
            item_name = Label(
                text=item['event'],
                font_size=sp(14),
                bold=True,
                size_hint=(0.7, 1), # Adjusted size_hint to make space for the remove button
                halign='left',
                color=black
            )
            item_name.bind(size=self._update_label)

            # BoxLayout for quantity and remove button
            qty_remove_layout = BoxLayout(size_hint=(0.3, 1), spacing=dp(5))

            item_qty = Label(
                text=f"x{item['quantity']}",
                font_size=sp(14),
                size_hint=(0.6, 1), # Adjusted size_hint for quantity
                halign='right',
                color=black
            )
            item_qty.bind(size=self._update_label)

            # Remove button
            remove_button = Button(
                text="X",
                font_size=sp(14),
                size_hint=(0.4, 1), # Adjusted size_hint for remove button
                background_normal="",
                background_color=(0.9, 0.2, 0.2, 1), # Red color for remove
                color=white,
                bold=True
            )
            # Bind the remove button to the void_item method
            remove_button.bind(on_press=lambda instance, item_to_remove=item: self.void_item(item_to_remove))

            qty_remove_layout.add_widget(item_qty)
            qty_remove_layout.add_widget(remove_button)

            item_header.add_widget(item_name)
            item_header.add_widget(qty_remove_layout) # Add the new layout


            item_details = Label(
                text=f"{item['tier']}, One-way",
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

    # Method to void an item from the transaction (renamed from remove_item_from_transaction)
    def void_item(self, item_to_remove):
        # Find and remove the item from the list
        # Create a new list without the item to ensure ListProperty observer is triggered
        self.transaction_items = [item for item in self.transaction_items if item != item_to_remove]

        self.update_items_display()
        self.calculate_totals() # Recalculate totals after voiding item
        self.update_total_display()


    # Method to calculate subtotal, tax, and total
    def calculate_totals(self):
        # Calculate subtotal
        subtotal = 0.0
        for item in self.transaction_items:
            # Ensure price is float
            price = float(item['price']) if isinstance(item['price'], Decimal) else item['price']
            subtotal += price * item['quantity']
        
        # Calculate tax
        tax = subtotal * TAX_RATE
        
        # Calculate discount amount
        discount_amount = 0.0
        if self.selected_discount and self.selected_discount.get('factor'):
            discount_amount = subtotal * (1 - float(self.selected_discount['factor']))
        
        # Update properties
        self.subtotal = subtotal
        self.tax = tax
        self.discount_amount = discount_amount
        self.total = subtotal + tax - discount_amount
        
        # Update display
        self.update_total_display()


    # Method to update the display of the total amounts
    def update_total_display(self):
        # Update all amount labels with float values
        self.subtotal_amount_label.text = f"₱{float(self.subtotal):,.2f}"
        self.tax_amount_label.text = f"₱{float(self.tax):,.2f}"
        self.discount_amount_label.text = f"-₱{float(self.discount_amount):,.2f}"
        self.total_amount_label.text = f"₱{float(self.total):,.2f}"
        
        # Update checkout button text
        self.checkout_btn.text = f"Checkout ₱{float(self.total):,.2f}"

    # Method to show the payment method popup
    def show_payment_method_popup(self, instance):
        popup = PaymentMethodPopup(transaction_panel=self)
        popup.open()

    # Method to set the selected payment method and update the button text
    def set_payment_method(self, method):
        self.selected_payment_method = method

    # Method to update the payment method button text
    def update_payment_method_button_text(self, instance, value):
        self.payment_method_button.text = value

    # Method to show the discount popup
    def show_discount_popup(self, instance):
        popup = DiscountPopup(transaction_panel=self, discounts_list=discounts)
        popup.open()

    # Method to set the selected discount and trigger recalculation
    def set_discount(self, discount):
        self.selected_discount = discount
        self.calculate_totals()
        self.update_total_display()


    # Method to process numpad input
    def process_numpad_input(self, value):
        if value == 'C':
            self.cash_tendered = "0.00"
        elif value == '00':
            # Handle appending '00', prevent leading zeros unless it's just "0"
            if self.cash_tendered == "0.00":
                 pass # Don't add '00' to "0.00"
            else:
                # Convert to float, multiply by 100, add 00, convert back to string
                # This handles potential decimal points if added later
                current_value = float(self.cash_tendered) * 100
                current_value = int(current_value) * 100 # Treat as integer for '00' append
                self.cash_tendered = f"{current_value/100:.2f}" # Convert back to string with 2 decimal places

        else: # Digits '0' through '9'
            # Append the digit, treating the current value as a number before formatting
            current_value = float(self.cash_tendered) * 100 # Convert to cents to avoid float issues
            current_value = int(current_value) * 10 + int(value) # Append the digit
            self.cash_tendered = f"{current_value/100:.2f}" # Convert back to string with 2 decimal places


    # Method to update the cash tendered display
    def update_cash_display(self, instance, value):
        try:
            # Format the string value as currency with 2 decimal places
            self.cash_amount_label.text = f"₱{float(value):,.2f}"
        except ValueError:
            # Handle cases where value might not be a valid float (e.g., empty string)
            self.cash_amount_label.text = "₱0.00"

    # New method to cancel the current transaction
    def cancel_transaction(self, instance):
        # Clear the transaction items list
        self.transaction_items = []
        # Reset the cash tendered amount
        self.cash_tendered = "0.00"
        # Reset the selected discount to 'No Discount'
        self.selected_discount = discounts[-1]
        # Update the items display
        self.update_items_display()
        # Recalculate and update the totals display
        self.calculate_totals()
        self.update_total_display()

    # New method to show the checkout confirmation popup
    def show_checkout_popup(self, instance):
        # Check if there are items in the transaction before showing the popup
        if not self.transaction_items:
            display_error_popup("Checkout Error", "There are no items in the current transaction.")
            return

        # Check if a payment method has been selected
        if self.selected_payment_method == "Payment Method": # Default unselected text
            display_error_popup("Checkout Error", "Please select a payment method before proceeding to checkout.")
            return

        # Check if cash tendered is sufficient for cash payments
        if self.selected_payment_method == "Cash":
            try:
                cash_tendered_float = float(self.cash_tendered)
                if cash_tendered_float < self.total:
                    display_error_popup("Payment Error", "Insufficient cash tendered for the total amount.")
                    return
            except ValueError:
                display_error_popup("Payment Error", "Invalid cash amount entered. Please use the numpad.")
                return

        popup = CheckoutPopup(transaction_panel=self)
        popup.open()


class MainScreen(Screen):
    def __init__(self, **kwargs):
        print('MainScreen __init__')
        super(MainScreen, self).__init__(**kwargs)

        # Create root layout
        self.root_layout = BoxLayout(orientation='vertical')

        # Create content layout (horizontal)
        self.content_layout = BoxLayout(orientation='horizontal', padding=[dp(20), dp(20), dp(20), dp(20)], spacing=dp(20))

        # Set background color
        with self.content_layout.canvas.before:
            Color(*gray_bg)
            Rectangle(size=self.content_layout.size, pos=self.content_layout.pos)
        self.content_layout.bind(size=self._update_bg, pos=self._update_bg)

        # Add route selector (left side) - pass transaction_panel instance
        self.route_selector = RouteSelector(transaction_panel=None, size_hint_x=0.75)
        self.content_layout.add_widget(self.route_selector)

        # Add transaction panel (right side) - instantiate first
        self.transaction_panel = TransactionPanel(size_hint_x=0.25)
        self.content_layout.add_widget(self.transaction_panel)

        # Now that transaction_panel is created, set it for route_selector
        self.route_selector.transaction_panel = self.transaction_panel

        self.root_layout.add_widget(self.content_layout)
        self.add_widget(self.root_layout)

    def on_enter(self):
        # Remove any existing navigation bar
        for child in self.root_layout.children[:]:
            if isinstance(child, (NavBar, UserNavBar)):
                self.root_layout.remove_widget(child)

        # Add the correct navigation bar at the top
        user = auth.getCurrentUser()
        if user.get('role') == 'admin':
            self.root_layout.add_widget(NavBar(), index=len(self.root_layout.children))
        else:
            self.root_layout.add_widget(UserNavBar(), index=len(self.root_layout.children))

        # Refresh filter tabs to reflect latest inventory
        self.route_selector.build_filter_tabs()
        # Refresh event cards to reflect latest inventory and filters
        self.route_selector.filter_routes()

    def _update_bg(self, instance, value):
        print('MainScreen _update_bg')
        # Only update the canvas, do NOT modify instance.size or instance.pos here!
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*gray_bg)
            Rectangle(size=instance.size, pos=instance.pos)