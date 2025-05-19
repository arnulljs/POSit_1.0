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

from datetime import datetime # Added
import xml.etree.ElementTree as ET # Added
import os # Added

import auth
from models import User, Admin
from adminInventory import AdminInventoryScreen
from adminNav import NavBar
from tickets import get_routes


class HomeScreen(Screen):
    """
    Home screen that checks user role and redirects to appropriate dashboard
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "home"
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical', padding=dp(20))
        
        # This will be populated on_enter
        self.add_widget(self.layout)
        
        # Add a white background
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            self.rect = Rectangle(size=self.size, pos=self.pos)
        Clock.schedule_once(lambda dt: self._update_rect(self, None), 0)
        self.bind(size=self._update_rect, pos=self._update_rect)
    
    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos
    
    def on_enter(self):
        # Clear previous widgets
        self.layout.clear_widgets()
        
        # Get current user session
        user_session = auth.getCurrentUser()
        
        if user_session["role"] == "admin":
            # If admin, redirect to admin dashboard
            # We use Clock.schedule_once to avoid screen transition issues
            Clock.schedule_once(lambda dt: self.redirect_to_admin(), 0.1)
        elif user_session["role"] == "user":
            # If regular user, show user dashboard
            self.setup_user_dashboard(user_session)
        else:
            # If no valid role, redirect to login
            Clock.schedule_once(lambda dt: self.redirect_to_login(), 0.1)
    
    def redirect_to_admin(self):
        if not self.manager.has_screen("admin_dashboard"):
            self.manager.add_widget(AdminDashboard(name="admin_dashboard"))
        self.manager.current = "admin_dashboard"
    
    def redirect_to_login(self):
        self.manager.current = "login"
    
    def setup_user_dashboard(self, user_session):
        welcome_label = Label(
            text=f"Welcome, {user_session['username']}!",
            font_size=dp(24),
            size_hint=(1, None),
            height=dp(50),
            color=(0, 0, 0, 1)
        )
        
        role_label = Label(
            text=f"Role: {user_session['role']}",
            font_size=dp(18),
            size_hint=(1, None),
            height=dp(30),
            color=(0, 0, 0, 0.7)
        )
        
        message_label = Label(
            text="This is the user dashboard. You don't have admin privileges.",
            font_size=dp(16),
            size_hint=(1, None),
            height=dp(60),
            color=(0, 0, 0, 0.8)
        )
        
        logout_btn = Button(
            text="Logout",
            size_hint=(None, None),
            size=(dp(150), dp(50)),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(0.22, 0.27, 0.74, 1),
            color=(1, 1, 1, 1)
        )
        logout_btn.bind(on_release=self.logout)
        
        self.layout.add_widget(welcome_label)
        self.layout.add_widget(role_label)
        self.layout.add_widget(message_label)
        self.layout.add_widget(BoxLayout(size_hint=(1, 1)))  # Spacer
        self.layout.add_widget(logout_btn)
    
    def logout(self, instance):
        auth.logout()
        self.manager.current = "login"


# Helper function to get transaction summary for the current day
def get_daily_transaction_summary():
    today_str = datetime.now().strftime("%Y-%m-%d")
    transactions_dir = "transactions"
    if not os.path.exists(transactions_dir):
        os.makedirs(transactions_dir)
    filename = os.path.join(transactions_dir, f"transactions_{today_str}.xml")
    total_sales = 0.0
    transaction_count = 0
    error_message = None

    if not os.path.exists(filename):
        error_message = f"File not found: {filename}"
        print(f"[AdminDashboard] {error_message}")
        return {'sales': total_sales, 'count': transaction_count, 'error': error_message}

    try:
        tree = ET.parse(filename)
        daily_root = tree.getroot()

        if daily_root.tag != "DailyTransactions":
            error_message = f"Invalid XML format in {filename}"
            print(f"[AdminDashboard] {error_message}")
            return {'sales': total_sales, 'count': transaction_count, 'error': error_message}

        for trans_elem in daily_root.findall("Transaction"):
            try:
                total_text = trans_elem.find("Summary/Total")
                if total_text is not None and total_text.text:
                    total_sales += float(total_text.text)
                transaction_count += 1
            except (ValueError, AttributeError) as e_item:
                print(f"[AdminDashboard] Warning: Skipping a transaction in {filename} due to item parsing error: {e_item}")
    except ET.ParseError as e_parse:
        error_message = f"Error parsing XML file {filename}: {e_parse}"
        print(f"[AdminDashboard] {error_message}")
    return {'sales': total_sales, 'count': transaction_count, 'error': error_message}


class MetricCard(BoxLayout):
    """
    Card widget for displaying a metric with title and value
    """
    def __init__(self, title, value, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (1, None)
        self.height = dp(120)
        self.padding = dp(15)
        
        # Add a white background with rounded corners
        with self.canvas.before:
            Color(1, 1, 1, 1)  # White background
            self.rect = RoundedRectangle(
                size=self.size, 
                pos=self.pos, 
                radius=[(dp(10), dp(10))] * 4
            )
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        # Value label with large font
        self.value_label = Label( # Made it an instance attribute
            text=str(value),
            font_size=dp(28),
            color=(0.22, 0.27, 0.74, 1),  # Blue color
            size_hint=(1, None),
            height=dp(50)
        )
        
        # Title label with smaller font
        self.title_label = Label( # Made it an instance attribute
            text=title,
            font_size=dp(14),
            color=(0, 0, 0, 0.7),  # Dark gray
            size_hint=(1, None),
            height=dp(30)
        )
        
        self.add_widget(self.value_label)
        self.add_widget(self.title_label)
    
    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos


class AlertItem(BoxLayout):
    """
    Widget for displaying an alert with severity indicated by color
    """
    def __init__(self, message, level='normal', **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (1, None)
        self.height = dp(60)
        self.padding = [dp(15), dp(10)]
        self.spacing = dp(10)
        
        # Set color based on level
        if level == 'critical':
            color = (0.9, 0.3, 0.3, 1)  # Red
        elif level == 'warning':
            color = (0.95, 0.6, 0.1, 1)  # Orange
        else:
            color = (0.3, 0.6, 0.9, 1)  # Blue
        self.indicator_color = color  # Store the color for later use
        
        # Add a colored indicator bar
        indicator = BoxLayout(
            size_hint=(None, 1),
            width=dp(5)
        )
        with indicator.canvas:
            Color(*color)
            Rectangle(pos=indicator.pos, size=indicator.size)
        indicator.bind(pos=self._update_indicator, size=self._update_indicator)
        
        # Message label
        message_label = Label(
            text=message,
            font_size=dp(14),
            color=(0, 0, 0, 0.8),
            halign='left',
            valign='middle',
            text_size=(None, dp(60))
        )
        
        self.add_widget(indicator)
        self.add_widget(message_label)
        
        # Add subtle background color
        with self.canvas.before:
            Color(0.98, 0.98, 0.98, 1)  # Very light gray
            self.rect = RoundedRectangle(
                size=self.size, 
                pos=self.pos, 
                radius=[(dp(5), dp(5))] * 4
            )
        self.bind(size=self._update_rect, pos=self._update_rect)
    
    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos
    
    def _update_indicator(self, instance, value):
        instance.canvas.clear()
        with instance.canvas:
            Color(*self.indicator_color)
            Rectangle(pos=instance.pos, size=instance.size)


class AdminDashboard(Screen):
    """
    Admin dashboard screen with metrics and system alerts
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "admin_dashboard"
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(0), spacing=dp(0))
        
        # Add NavBar (no arguments)
        main_layout.add_widget(NavBar())
        
        # Add a padded container for the dashboard content
        content_container = BoxLayout(orientation='vertical', padding=[dp(32), dp(16), dp(32), dp(16)], spacing=dp(16))
        
        # Header with title and logout button
        header = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(60))
        
        title_label = Label(
            text="Admin Dashboard",
            font_size=dp(24),
            color=(0, 0, 0, 1),
            size_hint=(1, 1),
            halign='left'
        )
        title_label.bind(size=self._update_text_size)
        
        logout_btn = Button(
            text="Logout",
            size_hint=(None, None),
            size=(dp(120), dp(40)),
            background_normal='',
            background_color=(0.22, 0.27, 0.74, 1),
            color=(1, 1, 1, 1)
        )
        logout_btn.bind(on_release=self.logout)
        
        header.add_widget(title_label)
        header.add_widget(logout_btn)
        
        # Subtitle
        subtitle = Label(
            text="Overview of system performance and key metrics",
            font_size=dp(14),
            color=(0, 0, 0, 0.7),
            size_hint=(1, None),
            height=dp(30),
            halign='left'
        )
        subtitle.bind(size=self._update_text_size)
        
        # Metrics section
        metrics_grid = GridLayout(
            cols=4,
            spacing=dp(15),
            size_hint=(1, None),
            height=dp(120)
        )
        
        # Fetch initial dynamic data
        summary_data = get_daily_transaction_summary()
        sales_val = summary_data.get('sales', 0.0)
        count_val = summary_data.get('count', 0)
        error_msg = summary_data.get('error')

        # Determine display values
        if error_msg and "File not found" not in error_msg: # An error occurred, and it's not 'File not found'
            initial_sales_value = "Error"
            initial_transactions_value = "Error"
        else: # No error, or 'File not found' (in which case sales_val and count_val are 0)
            initial_sales_value = f"₱{sales_val:,.2f}"
            initial_transactions_value = str(count_val)
            
        # Low and critical stock counts
        low_stock_count, critical_stock_count = count_low_and_critical_stock()

        # Create and store metric cards as instance variables
        self.sales_metric = MetricCard("Today's Sales", initial_sales_value)
        self.transactions_metric = MetricCard("Transactions Today", initial_transactions_value)
        self.low_stock_metric = MetricCard("Low Stock Items", str(low_stock_count))
        self.active_users_metric = MetricCard("Active Users", "12") # Static for now
        
        metrics_grid.add_widget(self.sales_metric)
        metrics_grid.add_widget(self.transactions_metric)
        metrics_grid.add_widget(self.low_stock_metric)
        metrics_grid.add_widget(self.active_users_metric)
        
        # System Alerts section
        alerts_title = Label(
            text="System Alerts",
            font_size=dp(18),
            color=(0, 0, 0, 1),
            size_hint=(1, None),
            height=dp(40),
            halign='left'
        )
        alerts_title.bind(size=self._update_text_size)
        
        # Create scrollable alerts container
        alerts_container = BoxLayout(orientation='vertical', spacing=dp(10), size_hint=(1, None))
        alerts_container.bind(minimum_height=alerts_container.setter('height'))
        
        # Sample alerts
        alerts = []
        if critical_stock_count > 0:
            alerts.append({
                "message": f"Critical Stock: {critical_stock_count} item(s) at or below 5 remaining!",
                "level": "critical"
            })
        if low_stock_count > 0:
            alerts.append({
                "message": f"Low Stock: {low_stock_count} item(s) at or below 10 remaining.",
                "level": "warning"
            })
        
        for alert in alerts:
            alert_item = AlertItem(alert["message"], alert["level"])
            alerts_container.add_widget(alert_item)
        
        # Create scrollview for alerts
        alerts_scroll = ScrollView(size_hint=(1, None), height=dp(200))
        alerts_scroll.add_widget(alerts_container)
        
        # Daily Sales Trend section
        trend_title = Label(
            text="Daily Sales Trend",
            font_size=dp(18),
            color=(0, 0, 0, 1),
            size_hint=(1, None),
            height=dp(40),
            halign='left'
        )
        trend_title.bind(size=self._update_text_size)
        
        # Placeholder for chart
        chart_placeholder = BoxLayout(size_hint=(1, 1))
        with chart_placeholder.canvas:
            Color(0.95, 0.95, 0.95, 1)  # Light gray
            RoundedRectangle(pos=chart_placeholder.pos, size=chart_placeholder.size, radius=[(dp(10), dp(10))] * 4)
        chart_placeholder.bind(pos=self._update_placeholder, size=self._update_placeholder)
        
        chart_label = Label(
            text="Sales chart visualization would appear here",
            font_size=dp(16),
            color=(0, 0, 0, 0.5)
        )
        chart_placeholder.add_widget(chart_label)
        
        # Add all sections to content_container
        content_container.add_widget(header)
        content_container.add_widget(subtitle)
        content_container.add_widget(metrics_grid)
        content_container.add_widget(alerts_title)
        content_container.add_widget(alerts_scroll)
        content_container.add_widget(trend_title)
        content_container.add_widget(chart_placeholder)
        
        # Add content_container to main_layout
        main_layout.add_widget(content_container)
        
        # Add everything to the screen
        self.add_widget(main_layout)
        
        # Add a white background
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        Clock.schedule_once(self._update_rect, 0)
    
    def on_enter(self):
        """Called when the screen is entered."""
        # Fetch fresh data for dynamic metric cards
        summary_data = get_daily_transaction_summary()
        sales_val = summary_data.get('sales', 0.0)
        count_val = summary_data.get('count', 0)
        error_msg = summary_data.get('error')

        # Determine display values
        if error_msg and "File not found" not in error_msg: # An error occurred, and it's not 'File not found'
            display_sales_value = "Error"
            display_transactions_value = "Error"
        else: # No error, or 'File not found' (in which case sales_val and count_val are 0)
            display_sales_value = f"₱{sales_val:,.2f}"
            display_transactions_value = str(count_val)

        # Update the text of the value labels in the metric cards
        if hasattr(self, 'sales_metric') and self.sales_metric:
            self.sales_metric.value_label.text = display_sales_value
        
        if hasattr(self, 'transactions_metric') and self.transactions_metric:
            self.transactions_metric.value_label.text = display_transactions_value

        if error_msg:
            print(f"[AdminDashboard] on_enter: Summary status: {error_msg}")

        # Note: Static metrics (low_stock, active_users) are not updated here.

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
    
    def _update_text_size(self, instance, value):
        instance.text_size = (instance.width, None)
    
    def _update_placeholder(self, instance, value):
        instance.canvas.clear()
        with instance.canvas:
            Color(0.95, 0.95, 0.95, 1)  # Light gray
            RoundedRectangle(pos=instance.pos, size=instance.size, radius=[(dp(10), dp(10))] * 4)
    
    def logout(self, instance):
        auth.logout()
        self.manager.current = "login"


def count_low_and_critical_stock():
    low_stock = 0
    critical_stock = 0
    for item in get_routes():
        try:
            avail = int(item.get('availability', 0))
            if avail <= 10:
                low_stock += 1
            if avail <= 5:
                critical_stock += 1
        except Exception:
            continue
    return low_stock, critical_stock