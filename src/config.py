"""
Configuration Management
========================

Loads configuration from environment variables using python-dotenv.
All sensitive data (passwords, API keys) should be in .env file,
NEVER committed to version control.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("⚠️ python-dotenv not installed. Using environment variables only.")


# Load .env file from project root
if DOTENV_AVAILABLE:
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded configuration from {env_path}")
    else:
        print(f"⚠️ No .env file found at {env_path}. Using defaults/environment.")


@dataclass(frozen=True)
class DatabaseConfig:
    """Database connection configuration.
    
    All values are loaded from environment variables with sensible defaults.
    
    Environment Variables:
        DB_HOST: Database host (default: localhost)
        DB_PORT: Database port (default: 3306)
        DB_NAME: Database name (default: ttr_db)
        DB_USER: Database user (default: root)
        DB_PASSWORD: Database password (REQUIRED in production!)
        DB_AUTH_PLUGIN: Authentication plugin (default: mysql_native_password)
    """
    
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "3306"))
    database: str = os.getenv("DB_NAME", "ttr_db")
    user: str = os.getenv("DB_USER", "root")
    password: str = os.getenv("DB_PASSWORD", "")
    auth_plugin: str = os.getenv("DB_AUTH_PLUGIN", "mysql_native_password")
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.password:
            print("⚠️ WARNING: DB_PASSWORD is empty! Database connection may fail.")
            print("   Please set DB_PASSWORD in your .env file.")
    
    def to_dict(self) -> dict[str, str | int]:
        """Convert to dictionary for mysql.connector.connect()."""
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'password': self.password,
            'auth_plugin': self.auth_plugin,
        }
    
    def __repr__(self) -> str:
        """Safe representation that hides the password."""
        return (
            f"DatabaseConfig("
            f"host='{self.host}', "
            f"port={self.port}, "
            f"database='{self.database}', "
            f"user='{self.user}', "
            f"password='***', "
            f"auth_plugin='{self.auth_plugin}')"
        )


@dataclass(frozen=True)
class AppConfig:
    """Application configuration.
    
    Environment Variables:
        APP_FULLSCREEN: Start in fullscreen mode (default: true)
        APP_DEBUG: Enable debug mode (default: false)
        APP_KIOSK_MODE: Enable kiosk mode (disable exit) (default: false)
    """
    
    fullscreen: bool = os.getenv("APP_FULLSCREEN", "true").lower() in ("true", "1", "yes")
    debug: bool = os.getenv("APP_DEBUG", "false").lower() in ("true", "1", "yes")
    kiosk_mode: bool = os.getenv("APP_KIOSK_MODE", "false").lower() in ("true", "1", "yes")
    
    # Paths
    project_root: Path = Path(__file__).parent.parent
    assets_dir: Path = project_root / "src" / "ui" / "resources"
    stylesheet_path: Path = assets_dir / "styles.qss"


# Singleton instances
db_config = DatabaseConfig()
app_config = AppConfig()


def get_db_config() -> DatabaseConfig:
    """Get the database configuration.
    
    Returns:
        DatabaseConfig instance
    """
    return db_config


def get_app_config() -> AppConfig:
    """Get the application configuration.
    
    Returns:
        AppConfig instance
    """
    return app_config


def reload_config() -> None:
    """Reload configuration from environment/dotenv.
    
    Useful for testing or dynamic configuration changes.
    """
    global db_config, app_config
    
    if DOTENV_AVAILABLE:
        load_dotenv(override=True)
    
    db_config = DatabaseConfig()
    app_config = AppConfig()
    
    print("✅ Configuration reloaded")


if __name__ == "__main__":
    # Test configuration loading
    print("=== Database Configuration ===")
    print(db_config)
    print("\n=== Application Configuration ===")
    print(f"Fullscreen: {app_config.fullscreen}")
    print(f"Debug: {app_config.debug}")
    print(f"Kiosk Mode: {app_config.kiosk_mode}")
    print(f"Stylesheet: {app_config.stylesheet_path}")
