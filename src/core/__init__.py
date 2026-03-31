"""
Core Business Logic Package
============================

This package contains pure Python business logic with NO PyQt6 dependencies.
All classes here are framework-agnostic and fully testable.
"""

from .constants import MatchMode, PageIndex, SETS_TO_WIN_MAP
from .models import Player, Match, Tournament, SetResult
from .match_engine import MatchEngine

__all__ = [
    'MatchMode',
    'PageIndex',
    'SETS_TO_WIN_MAP',
    'Player',
    'Match',
    'Tournament',
    'SetResult',
    'MatchEngine',
]
