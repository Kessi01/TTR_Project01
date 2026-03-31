"""
TTR - Table Tennis Referee
===========================

Main application entry point.

This is a TEMPORARY bootstrapper that will run the legacy ttr_gui.py
until all UI components are fully extracted and refactored.

Usage:
    python -m src.main
    # or
    python src/main.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import configuration
from src.config import get_app_config, get_db_config

# Import database
from src.database.connection import get_database_connection
from src.database.repository import create_repositories

# Import core (just to demonstrate it works)
from src.core.match_engine import MatchEngine
from src.core.constants import MatchMode, SETS_TO_WIN_MAP


def main() -> None:
    """Main application entry point."""
    print("=" * 60)
    print("TTR - Table Tennis Referee")
    print("=" * 60)
    print()
    
    # Load configuration
    app_config = get_app_config()
    db_config = get_db_config()
    
    print(f"📁 Project Root: {app_config.project_root}")
    print(f"🎨 Stylesheet: {app_config.stylesheet_path}")
    print(f"🗄️  Database: {db_config.database}@{db_config.host}")
    print()
    
    # Test database connection
    db = get_database_connection()
    if db.connect():
        print("✅ Database connected successfully!")
        
        # Create repositories
        player_repo, match_repo, tournament_repo = create_repositories(db)
        
        # Test: Load players
        players = player_repo.get_all()
        print(f"📊 Found {len(players)} players in database")
        
    else:
        print("⚠️  Running in offline mode (no database)")
        player_repo, match_repo, tournament_repo = create_repositories(use_dummy=True)
    
    print()
    print("=" * 60)
    print("🚧 NOTE: Full UI refactoring in progress!")
    print("   Currently using legacy ttr_gui.py")
    print("   New architecture components are ready:")
    print("   - ✅ Core Logic (MatchEngine)")
    print("   - ✅ Database Layer (Repository Pattern)")
    print("   - ✅ Configuration (Environment Variables)")
    print("   - ✅ UI Widgets (Confetti, Dialogs)")
    print("   - 🚧 Page Components (In Progress)")
    print("=" * 60)
    print()
    
    # TEMPORARY: Run legacy application
    print("🔄 Launching legacy GUI...")
    print()
    
    # Import and run legacy GUI
    from ttr_gui import main as legacy_main
    legacy_main()


if __name__ == "__main__":
    main()
