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

import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for Kivy
import matplotlib.pyplot as plt
import io
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image as KivyImage


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
        
        # Main layout: vertical, NavBar at top, content below
        main_layout = BoxLayout(orientation='vertical', spacing=0, padding=0)
        navbar = NavBar()
        navbar.size_hint_y = None
        navbar.height = dp(50)
        main_layout.add_widget(navbar)

        # Content area (no top padding)
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
        header.add_widget(title_label)
        
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
        self.active_users_metric = MetricCard("Active Users", "1") # Static for now
        
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
        self.alerts_container = BoxLayout(orientation='vertical', spacing=dp(10), size_hint=(1, None)) # Made instance variable
        self.alerts_container.bind(minimum_height=self.alerts_container.setter('height'))
        
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
            self.alerts_container.add_widget(alert_item)
        
        # Create scrollview for alerts
        alerts_scroll = ScrollView(size_hint=(1, None), height=dp(200))
        alerts_scroll.add_widget(self.alerts_container)
        
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
        
        # Chart box with padding and white rounded rectangle, wide and tall
        self.chart_box = BoxLayout(size_hint=(1, None), height=dp(320), padding=[dp(32), dp(24), dp(32), dp(24)])
        with self.chart_box.canvas.before:
            Color(1, 1, 1, 1)  # White
            self.chart_bg_rect = RoundedRectangle(pos=self.chart_box.pos, size=self.chart_box.size, radius=[(dp(24), dp(24))] * 4)
        self.chart_box.bind(pos=self._update_chart_bg, size=self._update_chart_bg)
        self.chart_img = KivyImage(allow_stretch=True, keep_ratio=True, size_hint=(1, 1))
        self.chart_box.add_widget(self.chart_img)
        self.update_sales_trend_graph()  # Draw initial graph
        
        # Add all sections to content_container
        content_container.add_widget(header)
        content_container.add_widget(subtitle)
        content_container.add_widget(metrics_grid)
        content_container.add_widget(alerts_title)
        content_container.add_widget(alerts_scroll)
        content_container.add_widget(trend_title)
        content_container.add_widget(self.chart_box)
        
        # At the end, add content_container to main_layout
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

        # Update low and critical stock counts and alerts
        low_stock_count, critical_stock_count = count_low_and_critical_stock()

        if hasattr(self, 'low_stock_metric') and self.low_stock_metric:
            self.low_stock_metric.value_label.text = str(low_stock_count)

        # Update alerts
        if hasattr(self, 'alerts_container') and self.alerts_container:
            self.alerts_container.clear_widgets()
            updated_alerts = []
            if critical_stock_count > 0:
                updated_alerts.append({
                    "message": f"Critical Stock: {critical_stock_count} item(s) at or below 5 remaining!",
                    "level": "critical"
                })
            if low_stock_count > 0: # This will include critical stock items as well if low_stock_count is just items <=10
                updated_alerts.append({
                    "message": f"Low Stock: {low_stock_count} item(s) at or below 10 remaining.", # Consider if this message should exclude critical items
                    "level": "warning"
                })
            for alert_data in updated_alerts:
                self.alerts_container.add_widget(AlertItem(alert_data["message"], alert_data["level"]))

        # Refresh the sales trend graph every time the screen is loaded
        self.update_sales_trend_graph()

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
    
    def _update_text_size(self, instance, value):
        instance.text_size = (instance.width, None)
    
    def _update_chart_bg(self, instance, value):
        self.chart_bg_rect.pos = instance.pos
        self.chart_bg_rect.size = instance.size
    
    def logout(self, instance):
        auth.logout()
        self.manager.current = "login"

    def update_sales_trend_graph(self):
        # Get today's transactions (from XML), or most recent if today's is missing
        from datetime import datetime
        import xml.etree.ElementTree as ET
        import os
        transactions_dir = "transactions"
        today_str = datetime.now().strftime("%Y-%m-%d")
        filename = os.path.join(transactions_dir, f"transactions_{today_str}.xml")
        # If today's file does not exist, use the most recent XML file
        most_recent_date = today_str
        if not os.path.exists(filename):
            xml_files = [f for f in os.listdir(transactions_dir) if f.startswith('transactions_') and f.endswith('.xml')]
            if xml_files:
                xml_files.sort(reverse=True)
                filename = os.path.join(transactions_dir, xml_files[0])
                # Extract date from filename (transactions_YYYY-MM-DD.xml)
                most_recent_date = xml_files[0].replace('transactions_', '').replace('.xml', '')
        sales_by_hour = {h: 0 for h in range(24)}
        if os.path.exists(filename):
            try:
                tree = ET.parse(filename)
                daily_root = tree.getroot()
                for trans_elem in daily_root.findall("Transaction"):
                    timestamp = trans_elem.findtext("Timestamp", "")
                    if timestamp:
                        try:
                            hour = int(timestamp.split()[1].split(":")[0])
                            sales_by_hour[hour] += 1
                        except Exception:
                            continue
            except Exception:
                pass
        hours = list(sales_by_hour.keys())
        counts = [sales_by_hour[h] for h in hours]
        # Plot with matplotlib
        plt.figure(figsize=(12, 3.5), facecolor='none')
        ax = plt.gca()
        ax.set_facecolor('none')  # Transparent axes background
        plt.plot(hours, counts, marker='o', color='#3944BC', linewidth=2)
        plt.title(f'Transactions per Hour ({most_recent_date})', fontsize=12)
        plt.xlabel('Hour of Day')
        plt.ylabel('Transactions')
        plt.xticks(range(0, 24, 1))
        plt.grid(True, linestyle='--', alpha=0.2)
        # Remove all spines (borders)
        for spine in ax.spines.values():
            spine.set_visible(False)
        # Remove axes frame
        ax.set_frame_on(False)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0.1)
        plt.close()
        buf.seek(0)
        im = CoreImage(buf, ext='png')
        buf.close()
        self.chart_img.texture = im.texture


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