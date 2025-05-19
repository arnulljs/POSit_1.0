# d:\POSit 1.0\reportsGUI.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from adminNav import NavBar # Assuming NavBar is in adminNav.py
from userNav import UserNavBar
import xml.etree.ElementTree as ET
import os
from datetime import datetime, timedelta
from kivy.uix.anchorlayout import AnchorLayout
import auth

ACCENT_BLUE = (0.22, 0.27, 0.74, 1)
WHITE = (1, 1, 1, 1)
BLACK = (0, 0, 0, 1)
LIGHT_GRAY_BG = (0.95, 0.95, 0.95, 1)
GRAY_BORDER = (0.7, 0.7, 0.7, 1)  # Gray color for borders
ROW_ALT_BLUE = (0.22, 0.27, 0.74, 0.08)  # Low opacity blue for alternating rows

class ReportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*LIGHT_GRAY_BG)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        self.layout = BoxLayout(orientation='vertical')
        self.navbar = None

        content_area = BoxLayout(orientation='vertical', padding=dp(32), spacing=dp(16), size_hint_y=1)
        self.content_area = content_area

        # Title
        title_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(60))
        title = Label(text='Transaction Reports', font_size=sp(24), bold=True, color=BLACK, halign='left', valign='bottom', size_hint_y=None, height=dp(30))
        title.bind(texture_size=title.setter('size'))
        title_layout.add_widget(title)
        subtitle = Label(text='View and generate sales and transaction reports', font_size=sp(14), color=(0,0,0,0.6), halign='left', valign='top', size_hint_y=None, height=dp(30))
        subtitle.bind(texture_size=subtitle.setter('size'))
        title_layout.add_widget(subtitle)
        content_area.add_widget(title_layout)

        # Date Input and Generate Button in a white container
        input_container = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100), padding=[dp(32), dp(24), dp(32), dp(24)])
        with input_container.canvas.before:
            Color(*WHITE)
            input_container.bg_rect = RoundedRectangle(size=input_container.size, pos=input_container.pos, radius=[(dp(10), dp(10))] * 4)
        input_container.bind(size=self._update_input_bg, pos=self._update_input_bg)

        input_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(18), padding=[0,0,0,0])
        # Large, left-aligned label
        input_label = Label(text='Report Date (YYYY-MM-DD):', color=ACCENT_BLUE, font_size=sp(22), bold=True, size_hint_x=None, width=dp(320), halign='left', valign='middle')
        input_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (instance.width, instance.height)))
        input_bar.add_widget(input_label)
        # Expanding TextInput
        self.date_input = TextInput(
            hint_text=datetime.now().strftime("%Y-%m-%d"),
            multiline=False,
            size_hint_x=1,
            width=0,
            height=dp(40),
            background_color=(0, 0, 0, 0),
            background_normal='',
            foreground_color=BLACK
        )
        input_bar.add_widget(self.date_input)
        # Fixed-width button
        generate_btn = Button(
            text='Generate Report',
            size_hint_x=None,
            width=dp(180),
            height=dp(40),
            background_normal='',
            background_color=ACCENT_BLUE,
            color=WHITE
        )
        generate_btn.bind(on_release=self.generate_report_for_date)
        input_bar.add_widget(generate_btn)
        # Center all vertically
        input_bar.padding = [0, (dp(56)-dp(40))//2, 0, (dp(56)-dp(40))//2]
        input_container.add_widget(input_bar)
        content_area.add_widget(input_container)

        # Report Display Area in a white container
        self.report_scrollview = ScrollView(size_hint=(1, 1), bar_width=dp(8))
        self.report_display_layout = BoxLayout(orientation='vertical', size_hint_y=1, spacing=dp(18), padding=[0, dp(10), 0, 0])
        self.report_scrollview.add_widget(self.report_display_layout)
        content_area.add_widget(self.report_scrollview)

        self.layout.add_widget(content_area)
        self.add_widget(self.layout)

        # Add a bottom border to the TextInput
        with self.date_input.canvas.after:
            Color(*GRAY_BORDER)
            self.date_input._bottom_border = Line(points=[], width=1.2)
        def update_bottom_border(instance, *args):
            x, y = instance.x, instance.y
            w = instance.width
            self.date_input._bottom_border.points = [x, y, x + w, y]
        self.date_input.bind(pos=update_bottom_border, size=update_bottom_border)

    def _update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def _update_input_bg(self, instance, value):
        instance.bg_rect.size = instance.size
        instance.bg_rect.pos = instance.pos

    def _update_report_bg(self, instance, value):
        instance.bg_rect.size = instance.size
        instance.bg_rect.pos = instance.pos

    def generate_report_for_date(self, instance):
        date_str = self.date_input.text.strip()
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            self.display_error("Invalid date format. Please use YYYY-MM-DD.")
            return

        report_data = self.fetch_transaction_data_for_day(date_str)
        self.display_daily_report(report_data, date_str)

    def fetch_transaction_data_for_day(self, date_str):
        # Ensure transactions folder exists
        transactions_dir = "transactions"
        if not os.path.exists(transactions_dir):
            os.makedirs(transactions_dir)
        filename = os.path.join(transactions_dir, f"transactions_{date_str}.xml")
        transactions = []
        summary = {
            "total_sales": 0.0,
            "total_tax": 0.0,
            "total_discount": 0.0,
            "transaction_count": 0
        }

        if not os.path.exists(filename):
            return {"error": f"No transactions found for {date_str} (File not found: {filename})"}

        try:
            tree = ET.parse(filename)
            daily_root = tree.getroot()

            if daily_root.tag != "DailyTransactions":
                return {"error": f"Invalid XML format in {filename}. Expected root tag 'DailyTransactions'."}

            for trans_elem in daily_root.findall("Transaction"):
                try:
                    tid = trans_elem.findtext("TransactionID", "N/A")
                    timestamp = trans_elem.findtext("Timestamp", "N/A")
                    total_text = trans_elem.find("Summary/Total")
                    tax_text = trans_elem.find("Summary/TaxAmount")
                    discount_text = trans_elem.find("Summary/DiscountAmount")

                    total = float(total_text.text) if total_text is not None and total_text.text else 0.0
                    tax = float(tax_text.text) if tax_text is not None and tax_text.text else 0.0
                    discount = float(discount_text.text) if discount_text is not None and discount_text.text else 0.0
                    
                    transactions.append({
                        "id": tid,
                        "timestamp": timestamp,
                        "total": total,
                        "tax": tax,
                        "discount": discount
                    })
                    summary["total_sales"] += total
                    summary["total_tax"] += tax
                    summary["total_discount"] += discount # Assuming discount is stored as positive
                    summary["transaction_count"] += 1
                except (ValueError, AttributeError) as e:
                    print(f"Warning: Skipping a transaction in {filename} due to parsing error: {e}")
                    transactions.append({
                        "id": "PARSE_ERROR",
                        "timestamp": "N/A",
                        "total": 0.0,
                        "error_details": str(e)
                    })


        except ET.ParseError:
            return {"error": f"Error parsing XML file: {filename}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred while processing {filename}: {str(e)}"}

        return {"summary": summary, "transactions": transactions}

    def display_daily_report(self, report_data, date_str):
        self.report_display_layout.clear_widgets()

        if report_data.get("error"):
            self.display_error(report_data["error"])
            return

        summary = report_data.get("summary", {})
        transactions = report_data.get("transactions", [])

        # Create a horizontal BoxLayout to hold both sections
        horizontal_layout = BoxLayout(orientation='horizontal', spacing=dp(18), size_hint_y=1)

        # Daily Sales Summary in its own rounded rectangle (sidebar)
        summary_container = BoxLayout(orientation='vertical', size_hint_x=0.35, size_hint_y=1, padding=dp(15), spacing=dp(5))
        with summary_container.canvas.before:
            Color(*WHITE)
            summary_container.bg_rect = RoundedRectangle(size=summary_container.size, pos=summary_container.pos, radius=[(dp(40), dp(40))] * 4)
        summary_container.bind(size=self._update_summary_bg, pos=self._update_summary_bg)

        # Inner vertical box for top-aligned content
        summary_content = BoxLayout(orientation='vertical', size_hint=(1, None), spacing=dp(5))
        summary_content.bind(minimum_height=summary_content.setter('height'))

        summary_title = Label(text=f"Daily Sales Summary for: {date_str}", font_size=sp(18), bold=True, color=BLACK, size_hint_y=None, height=dp(40), halign='center', valign='top')
        summary_title.bind(size=lambda instance, value: setattr(instance, 'text_size', (instance.width, None)))
        summary_content.add_widget(summary_title)

        summary_grid = GridLayout(cols=2, size_hint_y=None, spacing=dp(0), padding=[0, 0, 0, 0])
        summary_grid.bind(minimum_height=summary_grid.setter('height'))
        summary_grid.bind(minimum_height=lambda instance, value: setattr(instance, 'height', value))

        summary_items = [
            ("Total Transactions:", f"{summary.get('transaction_count', 0)}"),
            ("Total Sales:", f"₱{summary.get('total_sales', 0.0):,.2f}"),
            ("Total Tax Collected:", f"₱{summary.get('total_tax', 0.0):,.2f}"),
            ("Total Discounts Given:", f"₱{summary.get('total_discount', 0.0):,.2f}")
        ]
        for idx, (label_text, value_text) in enumerate(summary_items):
            row_color = WHITE if idx % 2 == 0 else ROW_ALT_BLUE
            label_cell = BoxLayout(size_hint_x=1, size_hint_y=None, height=dp(32), padding=[dp(8),0,dp(8),0])
            with label_cell.canvas.before:
                Color(*row_color)
                from kivy.graphics import Rectangle
                label_cell.bg_rect = Rectangle(pos=label_cell.pos, size=label_cell.size)
            label_cell.bind(pos=lambda instance, *args: setattr(instance.bg_rect, 'pos', instance.pos))
            label_cell.bind(size=lambda instance, *args: setattr(instance.bg_rect, 'size', instance.size))
            label = Label(text=label_text, color=BLACK, halign='right', valign='middle')
            label.bind(size=lambda instance, value: setattr(instance, 'text_size', instance.size))
            label_cell.add_widget(label)
            summary_grid.add_widget(label_cell)

            value_cell = BoxLayout(size_hint_x=1, size_hint_y=None, height=dp(32), padding=[dp(8),0,dp(8),0])
            with value_cell.canvas.before:
                Color(*row_color)
                value_cell.bg_rect = Rectangle(pos=value_cell.pos, size=value_cell.size)
            value_cell.bind(pos=lambda instance, *args: setattr(instance.bg_rect, 'pos', instance.pos))
            value_cell.bind(size=lambda instance, *args: setattr(instance.bg_rect, 'size', instance.size))
            value_label = Label(text=value_text, color=BLACK, halign='left', valign='middle')
            value_label.bind(size=lambda instance, value: setattr(instance, 'text_size', instance.size))
            value_cell.add_widget(value_label)
            summary_grid.add_widget(value_cell)
        summary_content.add_widget(summary_grid)
        summary_container.add_widget(summary_content)
        from kivy.uix.widget import Widget
        summary_container.add_widget(Widget(size_hint_y=1))

        # Individual Transactions in its own rounded rectangle (main area)
        from kivy.uix.anchorlayout import AnchorLayout
        trans_container = AnchorLayout(anchor_y='top', size_hint_x=0.65, size_hint_y=1, padding=dp(15))
        # Inner vertical box for top-anchored content
        trans_content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        trans_content.bind(minimum_height=trans_content.setter('height'))
        with trans_container.canvas.before:
            Color(*WHITE)
            trans_container.bg_rect = RoundedRectangle(size=trans_container.size, pos=trans_container.pos, radius=[(dp(40), dp(40))] * 4)
        trans_container.bind(size=self._update_trans_bg, pos=self._update_trans_bg)

        trans_title = Label(text="Individual Transactions:", font_size=sp(16), bold=True, color=BLACK, size_hint_y=None, height=dp(30), halign='center')
        trans_title.bind(size=lambda instance, value: setattr(instance, 'text_size', (instance.width, None)))
        trans_content.add_widget(trans_title)

        if transactions:
            # Header row
            trans_header_grid = GridLayout(cols=3, size_hint_y=None, height=dp(36), spacing=dp(0), padding=[0,0,0,0])
            headers = ["Transaction ID", "Timestamp", "Total Amount"]
            for h_text in headers:
                header_cell = BoxLayout(size_hint_x=1, size_hint_y=None, height=dp(36), padding=[dp(8),0,dp(8),0])
                with header_cell.canvas.before:
                    Color(*LIGHT_GRAY_BG)
                    header_cell.bg_rect = Rectangle(pos=header_cell.pos, size=header_cell.size)
                header_cell.bind(pos=lambda instance, *args: setattr(instance.bg_rect, 'pos', instance.pos))
                header_cell.bind(size=lambda instance, *args: setattr(instance.bg_rect, 'size', instance.size))
                header_cell.add_widget(Label(text=h_text, bold=True, color=BLACK, halign='center', valign='middle'))
                trans_header_grid.add_widget(header_cell)
            trans_content.add_widget(trans_header_grid)

            for idx, t in enumerate(transactions):
                row_color = WHITE if idx % 2 == 0 else ROW_ALT_BLUE
                if "error_details" in t:
                    row_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(32), padding=[dp(8),0,dp(8),0])
                    with row_layout.canvas.before:
                        Color(*row_color)
                        row_layout.bg_rect = Rectangle(pos=row_layout.pos, size=row_layout.size)
                    row_layout.bind(pos=lambda instance, *args: setattr(instance.bg_rect, 'pos', instance.pos))
                    row_layout.bind(size=lambda instance, *args: setattr(instance.bg_rect, 'size', instance.size))
                    row_layout.add_widget(Label(text=f"Error: {t['id']}", color=(0.8,0,0,1), halign='left'))
                    row_layout.add_widget(Label(text=f"Details: {t['error_details']}", color=(0.8,0,0,1), halign='left'))
                    trans_content.add_widget(row_layout)
                    continue

                row_grid = GridLayout(cols=3, size_hint_y=None, height=dp(32), spacing=dp(0), padding=[0,0,0,0])
                for i in range(3):
                    cell = BoxLayout(size_hint_x=1, size_hint_y=None, height=dp(32), padding=[dp(8),0,dp(8),0])
                    with cell.canvas.before:
                        Color(*row_color)
                        cell.bg_rect = Rectangle(pos=cell.pos, size=cell.size)
                    cell.bind(pos=lambda instance, *args: setattr(instance.bg_rect, 'pos', instance.pos))
                    cell.bind(size=lambda instance, *args: setattr(instance.bg_rect, 'size', instance.size))
                    if i == 0:
                        cell.add_widget(Label(text=t.get("id", "N/A"), color=BLACK, halign='center', valign='middle'))
                    elif i == 1:
                        cell.add_widget(Label(text=t.get("timestamp", "N/A"), color=BLACK, halign='center', valign='middle'))
                    else:
                        cell.add_widget(Label(text=f"₱{t.get('total', 0.0):,.2f}", color=BLACK, halign='right', valign='middle'))
                    row_grid.add_widget(cell)
                trans_content.add_widget(row_grid)
        else:
            no_trans_label = Label(text="No individual transactions to display for this day.", color=BLACK, size_hint_y=None, height=dp(30), halign='center')
            no_trans_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (instance.width, None)))
            trans_content.add_widget(no_trans_label)

        trans_container.add_widget(trans_content)

        # Add both containers to the horizontal layout (no AnchorLayout)
        horizontal_layout.add_widget(summary_container)
        horizontal_layout.add_widget(trans_container)
        self.report_display_layout.add_widget(horizontal_layout)

    def _update_summary_bg(self, instance, value):
        instance.bg_rect.size = instance.size
        instance.bg_rect.pos = instance.pos

    def _update_trans_bg(self, instance, value):
        instance.bg_rect.size = instance.size
        instance.bg_rect.pos = instance.pos

    def display_error(self, message):
        self.report_display_layout.clear_widgets()
        error_container = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100), padding=dp(15))
        with error_container.canvas.before:
            Color(*WHITE)
            error_container.bg_rect = RoundedRectangle(size=error_container.size, pos=error_container.pos, radius=[(dp(10), dp(10))] * 4)
        error_container.bind(size=self._update_error_bg, pos=self._update_error_bg)
        error_label = Label(text=message, color=(0.8, 0, 0, 1), font_size=sp(16), size_hint_y=None, height=dp(50), halign='center')
        error_container.add_widget(error_label)
        self.report_display_layout.add_widget(error_container)

    def _update_error_bg(self, instance, value):
        instance.bg_rect.size = instance.size
        instance.bg_rect.pos = instance.pos

    def on_pre_enter(self, *args):
        self.update_navbar()

    def update_navbar(self):
        # Remove existing navbar if present
        if self.navbar and self.navbar.parent:
            self.layout.remove_widget(self.navbar)
        # Determine current role
        role = auth.getCurrentUser().get('role', 'user')
        if role == 'admin':
            self.navbar = NavBar()
        else:
            self.navbar = UserNavBar()
        # Clear and re-add widgets in correct order
        self.layout.clear_widgets()
        self.layout.add_widget(self.navbar)
        self.layout.add_widget(self.content_area)

if __name__ == '__main__': # For testing this screen directly
    from kivy.app import App
    class TestApp(App):
        def build(self):
            # Create a dummy XML for testing if it doesn't exist
            today_str = datetime.now().strftime("%Y-%m-%d")
            transactions_dir = "transactions"
            if not os.path.exists(transactions_dir):
                os.makedirs(transactions_dir)
            dummy_xml_filename = os.path.join(transactions_dir, f"transactions_{today_str}.xml")
            if not os.path.exists(dummy_xml_filename):
                root = ET.Element("DailyTransactions")
                trans1 = ET.SubElement(root, "Transaction")
                ET.SubElement(trans1, "TransactionID").text = "00001"
                ET.SubElement(trans1, "Timestamp").text = f"{today_str} 10:00:00"
                summary1 = ET.SubElement(trans1, "Summary")
                ET.SubElement(summary1, "Total").text = "150.75"
                ET.SubElement(summary1, "TaxAmount").text = "15.75"
                ET.SubElement(summary1, "DiscountAmount").text = "10.00"

                trans2 = ET.SubElement(root, "Transaction")
                ET.SubElement(trans2, "TransactionID").text = "00002"
                ET.SubElement(trans2, "Timestamp").text = f"{today_str} 11:30:00"
                summary2 = ET.SubElement(trans2, "Summary")
                ET.SubElement(summary2, "Total").text = "220.50"
                ET.SubElement(summary2, "TaxAmount").text = "22.50"
                ET.SubElement(summary2, "DiscountAmount").text = "0.00"

                tree = ET.ElementTree(root)
                ET.indent(tree, space="\t", level=0)
                try:
                    tree.write(dummy_xml_filename, encoding="utf-8", xml_declaration=True)
                    print(f"Created dummy XML: {dummy_xml_filename}")
                except Exception as e:
                    print(f"Error creating dummy XML: {e}")

            return ReportScreen(name='reports_screen')
    TestApp().run()
