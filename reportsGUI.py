# d:\POSit 1.0\reportsGUI.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle
from adminNav import NavBar # Assuming NavBar is in adminNav.py
import xml.etree.ElementTree as ET
import os
from datetime import datetime, timedelta

ACCENT_BLUE = (0.22, 0.27, 0.74, 1)
WHITE = (1, 1, 1, 1)
BLACK = (0, 0, 0, 1)
LIGHT_GRAY_BG = (0.95, 0.95, 0.97, 1)

class ReportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*WHITE)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(NavBar())

        content_area = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        # Title
        title_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(60))
        title = Label(text='Transaction Reports', font_size=sp(20), bold=True, color=BLACK, halign='left', valign='bottom', size_hint_y=None, height=dp(30))
        title.bind(texture_size=title.setter('size'))
        title_layout.add_widget(title)
        subtitle = Label(text='View and generate sales and transaction reports', font_size=sp(14), color=(0,0,0,0.6), halign='left', valign='top', size_hint_y=None, height=dp(30))
        subtitle.bind(texture_size=subtitle.setter('size'))
        title_layout.add_widget(subtitle)
        content_area.add_widget(title_layout)

        # Date Input and Generate Button
        input_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        input_bar.add_widget(Label(text='Report Date (YYYY-MM-DD):', size_hint_x=0.4, color=BLACK))
        self.date_input = TextInput(
            hint_text=datetime.now().strftime("%Y-%m-%d"), # Default to today
            multiline=False,
            size_hint_x=0.4
        )
        input_bar.add_widget(self.date_input)
        generate_btn = Button(
            text='Generate Report',
            size_hint_x=0.2,
            background_color=ACCENT_BLUE,
            color=WHITE
        )
        generate_btn.bind(on_release=self.generate_report_for_date)
        input_bar.add_widget(generate_btn)
        content_area.add_widget(input_bar)

        # Report Display Area
        report_header = Label(text="Report Details", font_size=sp(16), bold=True, color=BLACK, size_hint_y=None, height=dp(30))
        content_area.add_widget(report_header)

        self.report_scrollview = ScrollView(size_hint=(1, 1))
        self.report_display_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        self.report_display_layout.bind(minimum_height=self.report_display_layout.setter('height'))
        self.report_scrollview.add_widget(self.report_display_layout)
        content_area.add_widget(self.report_scrollview)

        self.layout.add_widget(content_area)
        self.add_widget(self.layout)

    def _update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def generate_report_for_date(self, instance):
        date_str = self.date_input.text.strip()
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d") # Use today if input is empty

        try:
            # Validate date format
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            self.display_error("Invalid date format. Please use YYYY-MM-DD.")
            return

        report_data = self.fetch_transaction_data_for_day(date_str)
        self.display_daily_report(report_data, date_str)

    def fetch_transaction_data_for_day(self, date_str):
        filename = f"transactions_{date_str}.xml"
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

        # Summary Section
        summary_title = Label(text=f"Daily Sales Summary for: {date_str}", font_size=sp(18), bold=True, color=BLACK, size_hint_y=None, height=dp(35))
        self.report_display_layout.add_widget(summary_title)

        summary_grid = GridLayout(cols=2, size_hint_y=None, spacing=dp(5))
        summary_grid.bind(minimum_height=summary_grid.setter('height'))
        
        summary_items = [
            ("Total Transactions:", f"{summary.get('transaction_count', 0)}"),
            ("Total Sales:", f"₱{summary.get('total_sales', 0.0):,.2f}"),
            ("Total Tax Collected:", f"₱{summary.get('total_tax', 0.0):,.2f}"),
            ("Total Discounts Given:", f"₱{summary.get('total_discount', 0.0):,.2f}")
        ]
        for label_text, value_text in summary_items:
            summary_grid.add_widget(Label(text=label_text, color=BLACK, halign='left', size_hint_y=None, height=dp(25)))
            summary_grid.add_widget(Label(text=value_text, color=BLACK, halign='right', size_hint_y=None, height=dp(25)))
        self.report_display_layout.add_widget(summary_grid)

        self.report_display_layout.add_widget(Label(text="", size_hint_y=None, height=dp(10))) # Spacer

        # Transactions List Section
        if transactions:
            trans_title = Label(text="Individual Transactions:", font_size=sp(16), bold=True, color=BLACK, size_hint_y=None, height=dp(30))
            self.report_display_layout.add_widget(trans_title)

            trans_header_grid = GridLayout(cols=3, size_hint_y=None, height=dp(30), spacing=dp(2))
            headers = ["Transaction ID", "Timestamp", "Total Amount"]
            for h_text in headers:
                trans_header_grid.add_widget(Label(text=h_text, bold=True, color=BLACK))
            self.report_display_layout.add_widget(trans_header_grid)

            for t in transactions:
                if "error_details" in t: # Handle transactions that had parsing errors
                    row_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(25))
                    row_layout.add_widget(Label(text=f"Error: {t['id']}", color=(0.8,0,0,1), halign='left'))
                    row_layout.add_widget(Label(text=f"Details: {t['error_details']}", color=(0.8,0,0,1), halign='left'))
                    self.report_display_layout.add_widget(row_layout)
                    continue

                row_grid = GridLayout(cols=3, size_hint_y=None, height=dp(25), spacing=dp(2))
                row_grid.add_widget(Label(text=t.get("id", "N/A"), color=BLACK))
                row_grid.add_widget(Label(text=t.get("timestamp", "N/A"), color=BLACK))
                row_grid.add_widget(Label(text=f"₱{t.get('total', 0.0):,.2f}", color=BLACK, halign='right'))
                self.report_display_layout.add_widget(row_grid)
        else:
             self.report_display_layout.add_widget(Label(text="No individual transactions to display for this day.", color=BLACK, size_hint_y=None, height=dp(30)))


    def display_error(self, message):
        self.report_display_layout.clear_widgets()
        error_label = Label(text=message, color=(0.8, 0, 0, 1), font_size=sp(16), size_hint_y=None, height=dp(50), halign='center')
        self.report_display_layout.add_widget(error_label)

if __name__ == '__main__': # For testing this screen directly
    from kivy.app import App
    class TestApp(App):
        def build(self):
            # Create a dummy XML for testing if it doesn't exist
            today_str = datetime.now().strftime("%Y-%m-%d")
            dummy_xml_filename = f"transactions_{today_str}.xml"
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

