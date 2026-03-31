"""
Data Models
===========

Dataclasses for core domain entities.
These are framework-agnostic and can be easily serialized/tested.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Player:
    """Represents a table tennis player.
    
    Attributes:
        id: Database ID (None if not persisted yet)
        vorname: First name
        nachname: Last name
    """
    vorname: str
    nachname: str
    id: Optional[int] = None
    
    @property
    def full_name(self) -> str:
        """Returns the full name of the player."""
        return f"{self.vorname} {self.nachname}".strip()
    
    def __str__(self) -> str:
        return self.full_name


@dataclass
class Tournament:
    """Represents a tournament.
    
    Attributes:
        name: Tournament name
        sets_to_win: Number of sets required to win a match
        id: Database ID (None if not persisted yet)
        created_at: Creation timestamp
    """
    name: str
    sets_to_win: int = 3
    id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class Match:
    """Represents a completed match.
    
    Attributes:
        player1: First player
        player2: Second player
        sets_player1: Sets won by player 1
        sets_player2: Sets won by player 2
        tournament_id: Optional tournament reference
        id: Database ID (None if not persisted yet)
        match_date: When the match was played
    """
    player1: Player
    player2: Player
    sets_player1: int
    sets_player2: int
    tournament_id: Optional[int] = None
    id: Optional[int] = None
    match_date: Optional[datetime] = None
    
    @property
    def winner(self) -> Optional[Player]:
        """Returns the winning player, or None if tied."""
        if self.sets_player1 > self.sets_player2:
            return self.player1
        elif self.sets_player2 > self.sets_player1:
            return self.player2
        return None


@dataclass
class SetResult:
    """Result of adding a point to the match.
    
    This is returned by MatchEngine.add_point() to inform the UI
    about what happened (set won, match won, etc.).
    
    Attributes:
        set_won: True if a set was just won
        match_won: True if the match was just won
        winner: Player number (1 or 2) who won, or None
    """
    set_won: bool = False
    match_won: bool = False
    winner: Optional[int] = None


@dataclass
class MatchState:
    """Represents the complete state of an ongoing match.
    
    This is used for undo functionality and state persistence.
    
    Attributes:
        score_player1: Current score of player 1 in the current set
        score_player2: Current score of player 2 in the current set
        sets_player1: Sets won by player 1
        sets_player2: Sets won by player 2
        server: Current server (1 or 2)
    """
    score_player1: int
    score_player2: int
    sets_player1: int
    sets_player2: int
    server: int
