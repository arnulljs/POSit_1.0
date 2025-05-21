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

        transactions = report_data.get("transactions", [])

        # Outer card with white rounded rectangle
        from kivy.graphics import Color, RoundedRectangle
        card = BoxLayout(orientation='vertical', size_hint=(1, 1), padding=dp(15), spacing=dp(5))
        with card.canvas.before:
            Color(*WHITE)
            card.bg_rect = RoundedRectangle(size=card.size, pos=card.pos, radius=[(dp(18), dp(18))] * 4)
        card.bind(size=lambda instance, value: setattr(instance.bg_rect, 'size', instance.size))
        card.bind(pos=lambda instance, value: setattr(instance.bg_rect, 'pos', instance.pos))

        trans_header = Label(
            text="Transaction Details",
            font_size=sp(18), bold=True, color=BLACK,
            size_hint_y=None, height=dp(40), halign='center', valign='top'
        )
        trans_header.bind(size=lambda instance, value: setattr(instance, 'text_size', (instance.width, None)))
        card.add_widget(trans_header)

        # Table in a scrollview
        trans_grid = GridLayout(cols=4, size_hint_y=None, spacing=dp(0), padding=[0, 0, 0, 0])
        trans_grid.bind(minimum_height=trans_grid.setter('height'))

        headers = ["Transaction ID", "Timestamp", "Total", "Tax"]
        for header in headers:
            header_cell = BoxLayout(size_hint_y=None, height=dp(40), padding=[dp(8),0,dp(8),0])
            header_label = Label(text=header, color=ACCENT_BLUE, bold=True, halign='center', valign='middle')
            header_label.bind(size=lambda instance, value: setattr(instance, 'text_size', instance.size))
            header_cell.add_widget(header_label)
            trans_grid.add_widget(header_cell)

        for idx, trans in enumerate(transactions):
            row_color = WHITE if idx % 2 == 0 else ROW_ALT_BLUE
            cells = [
                trans.get('id', 'N/A'),
                trans.get('timestamp', 'N/A'),
                f"₱{trans.get('total', 0.0):,.2f}",
                f"₱{trans.get('tax', 0.0):,.2f}"
            ]
            for cell_text in cells:
                cell = BoxLayout(size_hint_y=None, height=dp(40), padding=[dp(8),0,dp(8),0])
                with cell.canvas.before:
                    Color(*row_color)
                    from kivy.graphics import Rectangle
                    cell.bg_rect = Rectangle(pos=cell.pos, size=cell.size)
                cell.bind(pos=lambda instance, *args: setattr(instance.bg_rect, 'pos', instance.pos))
                cell.bind(size=lambda instance, *args: setattr(instance.bg_rect, 'size', instance.size))
                label = Label(text=cell_text, color=BLACK, halign='center', valign='middle')
                label.bind(size=lambda instance, value: setattr(instance, 'text_size', instance.size))
                cell.add_widget(label)
                trans_grid.add_widget(cell)

        scroll = ScrollView(size_hint=(1, 1), bar_width=dp(8))
        scroll.add_widget(trans_grid)
        card.add_widget(scroll)

        self.report_display_layout.add_widget(card)

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
