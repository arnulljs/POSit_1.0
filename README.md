# POSit - Point of Sale System

A modern Point of Sale system built with Kivy and MySQL, designed for managing ticket sales and inventory.

## Features

- User authentication with role-based access control
- Ticket management system
- Transaction processing
- Admin dashboard with sales analytics
- Inventory management
- User management

## Prerequisites

- Python 3.8 or higher
- MySQL Server 8.0 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd posit
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```
```bash
pip install kivy[full]
```
```bash
pip install matplotlib
```

4. Set up the MySQL database:
   - Create a MySQL database named `posit_db`
   - Import the database schema:
```bash
mysql -u root -p posit_db < setup_database.sql
```

5. Configure database connection:
   - Open `db_config.py`
   - Update the `DB_CONFIG` dictionary with your MySQL credentials:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'posit_db'
}
```

## Running the Application

1. Activate the virtual environment (if not already activated):
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Run the application:
```bash
python main.py
```

## Default Login Credentials

- Admin:
  - Username: admin
  - Password: admin123

## Project Structure

- `main.py` - Application entry point
- `db_config.py` - Database configuration
- `models.py` - Data models
- `auth.py` - Authentication logic
- `tickets.py` - Ticket management
- `setup_database.sql` - Database schema
- GUI files:
  - `loginGUI.py`
  - `adminDashGUI.py`
  - `userGUI.py`
  - `reportsGUI.py`
  - `adminInventory.py`
  - `userManagement.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
