"""
Constants and Enumerations
===========================

All magic numbers and hardcoded values are replaced with named constants.
This improves code readability and maintainability.
"""

from enum import IntEnum
from typing import Final


class MatchMode(IntEnum):
    """Match mode selection for different game types."""
    QUICK = 0        # Quick match - single set
    BEST_OF_3 = 1    # Best of 3 - first to 2 sets
    BEST_OF_5 = 2    # Best of 5 - first to 3 sets
    BEST_OF_7 = 3    # Best of 7 - first to 4 sets
    TOURNAMENT = 4   # Tournament mode


class PageIndex(IntEnum):
    """Stack widget page indices for navigation."""
    START_MENU = 0
    MATCH_SETUP = 1
    TURNIER_LIST = 2
    TURNIER_DETAIL = 3
    SCOREBOARD = 4
    KEYBOARD = 5


# Match configuration
SETS_TO_WIN_MAP: Final[dict[MatchMode, int]] = {
    MatchMode.QUICK: 1,
    MatchMode.BEST_OF_3: 2,
    MatchMode.BEST_OF_5: 3,
    MatchMode.BEST_OF_7: 4,
}

# Game rules
POINTS_TO_WIN_SET: Final[int] = 11
POINTS_ADVANTAGE_REQUIRED: Final[int] = 2
SERVE_CHANGE_INTERVAL: Final[int] = 2  # Normal mode: every 2 points
DEUCE_THRESHOLD: Final[int] = 10        # When both players >= 10, serve changes every point

# Player identifiers
PLAYER_1: Final[int] = 1
PLAYER_2: Final[int] = 2

# Default values
DEFAULT_SETS_TO_WIN: Final[int] = 3  # Best of 5
DEFAULT_TOURNAMENT_NAME: Final[str] = "Neues Turnier"

# UI Constants
CONFETTI_PARTICLE_COUNT: Final[int] = 800
CONFETTI_FPS: Final[int] = 50
KEYBOARD_ROWS: Final[list[list[str]]] = [
    ['Q', 'W', 'E', 'R', 'T', 'Z', 'U', 'I', 'O', 'P', 'Ü'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Ö', 'Ä'],
    ['⇧', 'Y', 'X', 'C', 'V', 'B', 'N', 'M', '⌫'],
    ['←', '___SPACE___', '✓']
]
