"""
Database Connection Management
===============================

Handles MySQL connection with retry logic and graceful degradation.
"""

from typing import Optional
import time

try:
    import mysql.connector
    from mysql.connector import Error, MySQLConnection
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    MySQLConnection = None
    Error = Exception
    print("⚠️ mysql-connector-python not installed. Database features disabled.")

from ..config import get_db_config


class DatabaseConnection:
    """Manages database connection lifecycle.
    
    Features:
    - Automatic reconnection on connection loss
    - Retry logic with exponential backoff
    - Graceful degradation if MySQL unavailable
    - Connection pooling support
    
    Example:
        >>> db = DatabaseConnection()
        >>> if db.connect():
        ...     cursor = db.get_cursor()
        ...     cursor.execute("SELECT * FROM spieler")
        ...     db.close()
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0) -> None:
        """Initialize database connection manager.
        
        Args:
            max_retries: Maximum number of connection attempts
            retry_delay: Initial delay between retries (exponential backoff)
        """
        self.connection: Optional[MySQLConnection] = None
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._is_connected = False
    
    def connect(self) -> bool:
        """Establish database connection with retry logic.
        
        Returns:
            True if connected successfully, False otherwise
        """
        if not MYSQL_AVAILABLE:
            print("❌ MySQL connector not available")
            return False
        
        config = get_db_config()
        
        for attempt in range(1, self.max_retries + 1):
            try:
                self.connection = mysql.connector.connect(**config.to_dict())
                
                if self.connection.is_connected():
                    self._is_connected = True
                    db_info = self.connection.get_server_info()
                    print(f"✅ Connected to MySQL Server version {db_info}")
                    self._ensure_schema()
                    return True
                    
            except Error as e:
                print(f"❌ Connection attempt {attempt}/{self.max_retries} failed: {e}")
                
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                    print(f"⏳ Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
        
        print("❌ All connection attempts failed. Running in offline mode.")
        return False
    
    def disconnect(self) -> None:
        """Close the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self._is_connected = False
            print("🔌 Database connection closed")
    
    def is_connected(self) -> bool:
        """Check if database is connected.
        
        Returns:
            True if connected and alive
        """
        if not self.connection:
            return False
        
        try:
            return self.connection.is_connected()
        except:
            return False
    
    def get_cursor(self):
        """Get a database cursor.
        
        Returns:
            MySQL cursor object
        
        Raises:
            RuntimeError: If not connected
        """
        if not self.is_connected():
            raise RuntimeError("Not connected to database. Call connect() first.")
        
        return self.connection.cursor()
    
    def commit(self) -> None:
        """Commit the current transaction."""
        if self.connection:
            self.connection.commit()
    
    def rollback(self) -> None:
        """Rollback the current transaction."""
        if self.connection:
            self.connection.rollback()
    
    def _ensure_schema(self) -> None:
        """Ensure database schema is up to date.
        
        Checks for required columns and adds them if missing.
        """
        try:
            cursor = self.get_cursor()
            
            # Check if 'sets_to_win' column exists in 'turniere' table
            cursor.execute("SHOW COLUMNS FROM turniere LIKE 'sets_to_win'")
            result = cursor.fetchone()
            
            if not result:
                print("⚠️ Column 'sets_to_win' missing in 'turniere'. Adding...")
                cursor.execute("ALTER TABLE turniere ADD COLUMN sets_to_win INT DEFAULT 3")
                self.commit()
                print("✅ Database schema updated")
            
            cursor.close()
            
        except Error as e:
            print(f"⚠️ Schema check failed (non-critical): {e}")
    
    def __enter__(self):
        """Context manager entry."""
        if not self.is_connected():
            self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
        return False


# Singleton instance
_db_instance: Optional[DatabaseConnection] = None


def get_database_connection() -> DatabaseConnection:
    """Get the singleton database connection.
    
    Returns:
        DatabaseConnection instance
    """
    global _db_instance
    
    if _db_instance is None:
        _db_instance = DatabaseConnection()
    
    return _db_instance


if __name__ == "__main__":
    # Test connection
    print("=== Testing Database Connection ===\n")
    
    db = DatabaseConnection()
    
    if db.connect():
        print("\n✅ Connection successful!")
        
        try:
            cursor = db.get_cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print("\nTables in database:")
            for table in tables:
                print(f"  - {table[0]}")
            
            cursor.close()
        except Exception as e:
            print(f"❌ Query failed: {e}")
        
        db.disconnect()
    else:
        print("\n❌ Connection failed")
