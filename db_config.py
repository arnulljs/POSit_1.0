import mysql.connector
from mysql.connector import pooling
import logging
import time
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'sql12.freesqldatabase.com',
    'user': 'sql12780094',
    'password': 'd293VM7qBK',
    'database': 'sql12780094',
    'port': 3306,
    'connect_timeout': 10,  # Connection timeout in seconds
    'connection_timeout': 10,  # Timeout for operations
    'pool_reset_session': True,  # Reset session variables when connection is returned to pool
    'pool_name': 'mypool',
    'pool_size': 5,
    'use_pure': True,  # Use pure Python implementation for better error handling
}

# Global connection pool
connection_pool = None

def init_connection_pool():
    """Initialize the connection pool with retry mechanism."""
    global connection_pool
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            connection_pool = mysql.connector.pooling.MySQLConnectionPool(**DB_CONFIG)
            logger.info("Connection pool created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating connection pool (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error("Failed to create connection pool after all retries")
                return False

def get_db_connection():
    """Get a connection from the pool with retry mechanism."""
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            if connection_pool:
                conn = connection_pool.get_connection()
                # Validate connection
                if not conn.is_connected():
                    conn.reconnect(attempts=3, delay=1)
                return conn
            else:
                # Fallback to direct connection if pool creation failed
                return mysql.connector.connect(**DB_CONFIG)
        except Exception as e:
            logger.error(f"Error getting database connection (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise

def close_db_connection(connection):
    """Return a connection to the pool safely."""
    try:
        if connection and connection.is_connected():
            connection.close()
    except Exception as e:
        logger.error(f"Error closing database connection: {e}")

def with_db_retry(max_retries=3, retry_delay=1):
    """Decorator for retrying database operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except mysql.connector.Error as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Database operation failed (attempt {attempt + 1}/{max_retries}): {e}")
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"Database operation failed after all retries: {e}")
                        raise
            raise last_error
        return wrapper
    return decorator

@with_db_retry()
def execute_query(query, params=None, fetch=False):
    """Execute a database query using a connection from the pool."""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        if fetch:
            result = cursor.fetchall()
        else:
            connection.commit()
            result = None
            
        return result
    except Exception as e:
        if connection:
            connection.rollback()
        logger.error(f"Error executing query: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            close_db_connection(connection)

# Initialize connection pool on module import
init_connection_pool() 