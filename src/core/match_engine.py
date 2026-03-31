"""
Match Engine - Core Business Logic
===================================

This module contains the pure business logic for table tennis matches.
NO PyQt6 dependencies - fully testable and framework-agnostic.

The MatchEngine handles:
- Point tracking
- Set tracking
- Serve rotation according to official rules
- Win conditions
- Undo functionality
"""

from typing import Optional
from .models import Player, SetResult, MatchState
from .constants import (
    POINTS_TO_WIN_SET,
    POINTS_ADVANTAGE_REQUIRED,
    SERVE_CHANGE_INTERVAL,
    DEUCE_THRESHOLD,
    PLAYER_1,
    PLAYER_2,
    DEFAULT_SETS_TO_WIN,
)


class MatchEngine:
    """Manages the state and rules of a table tennis match.
    
    This class is completely independent of the UI layer and can be
    tested without any PyQt6 dependencies.
    
    Example:
        >>> engine = MatchEngine(player1_name="Alice", player2_name="Bob", sets_to_win=3)
        >>> result = engine.add_point(PLAYER_1)
        >>> if result.set_won:
        ...     print(f"Set won by player {result.winner}!")
    """
    
    def __init__(
        self,
        player1_name: str = "Spieler 1",
        player2_name: str = "Spieler 2",
        sets_to_win: int = DEFAULT_SETS_TO_WIN,
        initial_server: int = PLAYER_1,
    ) -> None:
        """Initialize a new match.
        
        Args:
            player1_name: Name of player 1
            player2_name: Name of player 2
            sets_to_win: Number of sets needed to win the match
            initial_server: Who serves first (PLAYER_1 or PLAYER_2)
        
        Raises:
            ValueError: If sets_to_win < 1 or initial_server not in {1, 2}
        """
        if sets_to_win < 1:
            raise ValueError("sets_to_win must be at least 1")
        if initial_server not in {PLAYER_1, PLAYER_2}:
            raise ValueError(f"initial_server must be {PLAYER_1} or {PLAYER_2}")
        
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.sets_to_win = sets_to_win
        
        # Current set scores
        self.score_player1 = 0
        self.score_player2 = 0
        
        # Sets won
        self.sets_player1 = 0
        self.sets_player2 = 0
        
        # Serve tracking
        self.server = initial_server
        self.initial_server = initial_server
        
        # History for undo (stack of MatchState)
        self._history: list[MatchState] = []
    
    def add_point(self, player: int) -> SetResult:
        """Add a point for the specified player.
        
        This method:
        1. Saves current state to history (for undo)
        2. Increments the score
        3. Checks for serve change
        4. Checks for set/match win
        
        Args:
            player: PLAYER_1 or PLAYER_2
        
        Returns:
            SetResult indicating if a set or match was won
        
        Raises:
            ValueError: If player is not PLAYER_1 or PLAYER_2
        """
        if player not in {PLAYER_1, PLAYER_2}:
            raise ValueError(f"player must be {PLAYER_1} or {PLAYER_2}")
        
        # Save state for undo
        self._save_state()
        
        # Add point
        if player == PLAYER_1:
            self.score_player1 += 1
        else:
            self.score_player2 += 1
        
        # Check serve change
        self._update_server()
        
        # Check for set win
        set_winner = self._check_set_win()
        match_winner = None
        
        if set_winner is not None:
            # Set won!
            if set_winner == PLAYER_1:
                self.sets_player1 += 1
            else:
                self.sets_player2 += 1
            
            # Check for match win
            match_winner = self._check_match_win()
        
        return SetResult(
            set_won=(set_winner is not None),
            match_won=(match_winner is not None),
            winner=set_winner if set_winner is not None else match_winner,
        )
    
    def undo_last_point(self) -> bool:
        """Undo the last point.
        
        Returns:
            True if undo was successful, False if no history available
        """
        if not self._history:
            return False
        
        state = self._history.pop()
        self.score_player1 = state.score_player1
        self.score_player2 = state.score_player2
        self.sets_player1 = state.sets_player1
        self.sets_player2 = state.sets_player2
        self.server = state.server
        
        return True
    
    def reset_set(self) -> None:
        """Reset the current set (after a set win).
        
        This is called after showing the set won dialog.
        The serve switches to the other player.
        """
        self.score_player1 = 0
        self.score_player2 = 0
        
        # Switch initial server for next set
        self.initial_server = PLAYER_2 if self.initial_server == PLAYER_1 else PLAYER_1
        self.server = self.initial_server
    
    def get_current_state(self) -> MatchState:
        """Get the current match state.
        
        Returns:
            MatchState snapshot of current scores and server
        """
        return MatchState(
            score_player1=self.score_player1,
            score_player2=self.score_player2,
            sets_player1=self.sets_player1,
            sets_player2=self.sets_player2,
            server=self.server,
        )
    
    def _save_state(self) -> None:
        """Save current state to history."""
        self._history.append(self.get_current_state())
    
    def _update_server(self) -> None:
        """Update the server based on official table tennis rules.
        
        Rules:
        - During normal play (< 10:10): serve changes every 2 points
        - During deuce (>= 10:10): serve changes every point
        """
        total_points = self.score_player1 + self.score_player2
        
        # Deuce: both players have at least 10 points
        if self.score_player1 >= DEUCE_THRESHOLD and self.score_player2 >= DEUCE_THRESHOLD:
            # Change serve every point
            self.server = PLAYER_2 if self.server == PLAYER_1 else PLAYER_1
        else:
            # Normal play: change every 2 points
            # We check if we just hit a multiple of SERVE_CHANGE_INTERVAL
            if total_points > 0 and total_points % SERVE_CHANGE_INTERVAL == 0:
                self.server = PLAYER_2 if self.server == PLAYER_1 else PLAYER_1
    
    def _check_set_win(self) -> Optional[int]:
        """Check if a player has won the current set.
        
        Win conditions:
        - Score >= POINTS_TO_WIN_SET (11)
        - Lead by at least POINTS_ADVANTAGE_REQUIRED (2)
        
        Returns:
            PLAYER_1, PLAYER_2, or None if no winner yet
        """
        if self.score_player1 >= POINTS_TO_WIN_SET:
            if self.score_player1 - self.score_player2 >= POINTS_ADVANTAGE_REQUIRED:
                return PLAYER_1
        
        if self.score_player2 >= POINTS_TO_WIN_SET:
            if self.score_player2 - self.score_player1 >= POINTS_ADVANTAGE_REQUIRED:
                return PLAYER_2
        
        return None
    
    def _check_match_win(self) -> Optional[int]:
        """Check if a player has won the match.
        
        Returns:
            PLAYER_1, PLAYER_2, or None if match continues
        """
        if self.sets_player1 >= self.sets_to_win:
            return PLAYER_1
        
        if self.sets_player2 >= self.sets_to_win:
            return PLAYER_2
        
        return None
    
    def is_match_finished(self) -> bool:
        """Check if the match is finished.
        
        Returns:
            True if either player has won the required number of sets
        """
        return self._check_match_win() is not None
    
    def get_winner(self) -> Optional[int]:
        """Get the match winner.
        
        Returns:
            PLAYER_1, PLAYER_2, or None if match not finished
        """
        return self._check_match_win()
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"MatchEngine("
            f"{self.player1_name}={self.score_player1}:{self.sets_player1}, "
            f"{self.player2_name}={self.score_player2}:{self.sets_player2}, "
            f"server={self.server})"
        )
