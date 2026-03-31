"""
Database Package
================

Handles all database interactions with abstraction for testability.
"""

from .connection import DatabaseConnection, get_database_connection
from .repository import (
    PlayerRepository,
    MatchRepository,
    TournamentRepository,
    MySQLPlayerRepository,
    MySQLMatchRepository,
    MySQLTournamentRepository,
    DummyPlayerRepository,
    DummyMatchRepository,
    DummyTournamentRepository,
)

__all__ = [
    'DatabaseConnection',
    'get_database_connection',
    'PlayerRepository',
    'MatchRepository',
    'TournamentRepository',
    'MySQLPlayerRepository',
    'MySQLMatchRepository',
    'MySQLTournamentRepository',
    'DummyPlayerRepository',
    'DummyMatchRepository',
    'DummyTournamentRepository',
]
