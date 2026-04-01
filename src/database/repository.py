"""
Database Repositories
=====================

Abstract repository interfaces and implementations for data access.
Uses Protocol for dependency injection and testability.

Implementations:
- MySQL: Real database access
- Dummy: Fake data for offline mode / testing
"""

from typing import Protocol, List, Optional, Tuple
from datetime import datetime

try:
    from mysql.connector import Error
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    Error = Exception

from ..core.models import Player, Match, Tournament
from .connection import DatabaseConnection


# ============================================================================
# Repository Protocols (Interfaces)
# ============================================================================

class PlayerRepository(Protocol):
    """Interface for player data access."""
    
    def get_all(self) -> List[Tuple[int, str, str]]:
        """Get all players as (id, vorname, nachname) tuples."""
        ...
    
    def get_or_create(self, full_name: str) -> Optional[int]:
        """Get player ID by name, or create if doesn't exist.
        
        Args:
            full_name: Full name ("Vorname Nachname")
        
        Returns:
            Player ID, or None if error
        """
        ...


class MatchRepository(Protocol):
    """Interface for match data access."""

    def save(
        self,
        player1_id: int,
        player2_id: int,
        sets_player1: int,
        sets_player2: int,
        tournament_id: Optional[int] = None,
        set_scores: Optional[List[Tuple[int, int]]] = None,
    ) -> Optional[int]:
        """Save a completed match including optional per-set scores.

        Args:
            set_scores: List of (points_p1, points_p2) per set in order.

        Returns:
            match_id if successful, None on error
        """
        ...

    def get_by_tournament(self, tournament_id: int) -> List[Tuple]:
        """Get all matches for a tournament.

        Returns:
            List of (match_id, player1_name, player2_name, score1, score2, date)
        """
        ...

    def get_set_scores(self, match_id: int) -> List[Tuple[int, int, int]]:
        """Get per-set scores for a match.

        Returns:
            List of (set_nummer, punkte_s1, punkte_s2)
        """
        ...


class TournamentRepository(Protocol):
    """Interface for tournament data access."""
    
    def get_all(self) -> List[Tuple[int, str, datetime, int]]:
        """Get all tournaments as (id, name, created_at, sets_to_win)."""
        ...
    
    def create(self, name: str, sets_to_win: int = 3) -> Optional[int]:
        """Create a new tournament.
        
        Returns:
            Tournament ID, or None if error
        """
        ...
    
    def get_rankings(self, tournament_id: int) -> List[Tuple[str, int, int]]:
        """Get player rankings for a tournament.
        
        Returns:
            List of (player_name, wins, losses) sorted by wins
        """
        ...


# ============================================================================
# MySQL Implementations
# ============================================================================

class MySQLPlayerRepository:
    """MySQL implementation of PlayerRepository."""
    
    def __init__(self, db: DatabaseConnection) -> None:
        self.db = db
    
    def get_all(self) -> List[Tuple[int, str, str]]:
        """Get all players from database."""
        try:
            cursor = self.db.get_cursor()
            cursor.execute(
                "SELECT id, vorname, nachname FROM spieler ORDER BY vorname, nachname"
            )
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"❌ Error loading players: {e}")
            return []
    
    def get_or_create(self, full_name: str) -> Optional[int]:
        """Get player by name or create new."""
        name_parts = full_name.strip().split(' ', 1)
        vorname = name_parts[0] if name_parts else full_name
        nachname = name_parts[1] if len(name_parts) > 1 else ""
        
        try:
            cursor = self.db.get_cursor()
            
            # Check if exists
            query_select = "SELECT id FROM spieler WHERE vorname = %s AND nachname = %s"
            cursor.execute(query_select, (vorname, nachname))
            result = cursor.fetchone()
            
            if result:
                cursor.close()
                return result[0]
            
            # Create new
            query_insert = "INSERT INTO spieler (vorname, nachname) VALUES (%s, %s)"
            cursor.execute(query_insert, (vorname, nachname))
            self.db.commit()
            player_id = cursor.lastrowid
            cursor.close()
            
            print(f"✅ New player created: {full_name}")
            return player_id
            
        except Error as e:
            print(f"❌ Error with player '{full_name}': {e}")
            return None


class MySQLMatchRepository:
    """MySQL implementation of MatchRepository."""

    def __init__(self, db: DatabaseConnection) -> None:
        self.db = db

    def save(
        self,
        player1_id: int,
        player2_id: int,
        sets_player1: int,
        sets_player2: int,
        tournament_id: Optional[int] = None,
        set_scores: Optional[List[Tuple[int, int]]] = None,
    ) -> Optional[int]:
        """Save match and optional per-set scores. Returns match_id or None."""
        try:
            cursor = self.db.get_cursor()
            query = """
                INSERT INTO matches
                (spieler1_id, spieler2_id, satz_score_s1, satz_score_s2, turnier_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (player1_id, player2_id, sets_player1, sets_player2, tournament_id)
            )
            self.db.commit()
            match_id = cursor.lastrowid
            cursor.close()

            if set_scores and match_id:
                self._save_set_scores(match_id, set_scores)

            print(f"✅ Match saved: {sets_player1}-{sets_player2}")
            return match_id

        except Error as e:
            print(f"❌ Error saving match: {e}")
            self.db.rollback()
            return None

    def _save_set_scores(self, match_id: int, set_scores: List[Tuple[int, int]]) -> None:
        """Insert per-set scores into match_sets."""
        try:
            cursor = self.db.get_cursor()
            for i, (p1, p2) in enumerate(set_scores, start=1):
                cursor.execute(
                    "INSERT INTO match_sets (match_id, set_nummer, punkte_s1, punkte_s2) VALUES (%s, %s, %s, %s)",
                    (match_id, i, p1, p2)
                )
            self.db.commit()
            cursor.close()
        except Error as e:
            print(f"❌ Error saving set scores: {e}")

    def get_by_tournament(self, tournament_id: int) -> List[Tuple]:
        """Get all matches for a tournament."""
        try:
            cursor = self.db.get_cursor()
            query = """
                SELECT m.id,
                       CONCAT(s1.vorname, ' ', s1.nachname) as player1,
                       CONCAT(s2.vorname, ' ', s2.nachname) as player2,
                       m.satz_score_s1, m.satz_score_s2, m.datum
                FROM matches m
                JOIN spieler s1 ON m.spieler1_id = s1.id
                JOIN spieler s2 ON m.spieler2_id = s2.id
                WHERE m.turnier_id = %s
                ORDER BY m.datum DESC
            """
            cursor.execute(query, (tournament_id,))
            result = cursor.fetchall()
            cursor.close()
            return result

        except Error as e:
            print(f"❌ Error loading matches: {e}")
            return []

    def get_set_scores(self, match_id: int) -> List[Tuple[int, int, int]]:
        """Get per-set scores for a match."""
        try:
            cursor = self.db.get_cursor()
            cursor.execute(
                "SELECT set_nummer, punkte_s1, punkte_s2 FROM match_sets WHERE match_id = %s ORDER BY set_nummer",
                (match_id,)
            )
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"❌ Error loading set scores: {e}")
            return []


class MySQLTournamentRepository:
    """MySQL implementation of TournamentRepository."""
    
    def __init__(self, db: DatabaseConnection) -> None:
        self.db = db
    
    def get_all(self) -> List[Tuple[int, str, datetime, int]]:
        """Get all tournaments."""
        try:
            cursor = self.db.get_cursor()
            cursor.execute(
                "SELECT id, name, erstellt_am, sets_to_win "
                "FROM turniere ORDER BY erstellt_am DESC"
            )
            result = cursor.fetchall()
            cursor.close()
            return result
            
        except Error as e:
            print(f"❌ Error loading tournaments: {e}")
            return []
    
    def create(self, name: str, sets_to_win: int = 3) -> Optional[int]:
        """Create a new tournament."""
        try:
            cursor = self.db.get_cursor()
            cursor.execute(
                "INSERT INTO turniere (name, sets_to_win) VALUES (%s, %s)",
                (name, sets_to_win)
            )
            self.db.commit()
            tournament_id = cursor.lastrowid
            cursor.close()
            
            print(f"✅ Tournament created: {name}")
            return tournament_id
            
        except Error as e:
            print(f"❌ Error creating tournament: {e}")
            self.db.rollback()
            return None
    
    def get_rankings(self, tournament_id: int) -> List[Tuple]:
        """Get player rankings for a tournament.

        Returns:
            List of (name, wins, losses, sets_won, sets_lost, set_diff)
        """
        try:
            cursor = self.db.get_cursor()
            query = """
                SELECT name, wins, losses, sets_won, sets_lost,
                       (sets_won - sets_lost) as set_diff
                FROM (
                    SELECT
                        CONCAT(s.vorname, ' ', s.nachname) as name,
                        SUM(CASE
                            WHEN (m.spieler1_id = s.id AND m.satz_score_s1 > m.satz_score_s2)
                              OR (m.spieler2_id = s.id AND m.satz_score_s2 > m.satz_score_s1)
                            THEN 1 ELSE 0 END) as wins,
                        SUM(CASE
                            WHEN (m.spieler1_id = s.id AND m.satz_score_s1 < m.satz_score_s2)
                              OR (m.spieler2_id = s.id AND m.satz_score_s2 < m.satz_score_s1)
                            THEN 1 ELSE 0 END) as losses,
                        SUM(CASE WHEN m.spieler1_id = s.id THEN m.satz_score_s1
                                 ELSE m.satz_score_s2 END) as sets_won,
                        SUM(CASE WHEN m.spieler1_id = s.id THEN m.satz_score_s2
                                 ELSE m.satz_score_s1 END) as sets_lost
                    FROM spieler s
                    JOIN matches m ON s.id = m.spieler1_id OR s.id = m.spieler2_id
                    WHERE m.turnier_id = %s
                    GROUP BY s.id, s.vorname, s.nachname
                ) as stats
                ORDER BY wins DESC, set_diff DESC
            """
            cursor.execute(query, (tournament_id,))
            result = cursor.fetchall()
            cursor.close()
            return result

        except Error as e:
            print(f"❌ Error loading rankings: {e}")
            return []


# ============================================================================
# Dummy Implementations (for offline mode / testing)
# ============================================================================

class DummyPlayerRepository:
    """Fake player repository for offline mode."""
    
    def __init__(self) -> None:
        self._players = [
            (1, "Max", "Mustermann"),
            (2, "Anna", "Schmidt"),
            (3, "Peter", "Mueller"),
        ]
        self._next_id = 4
    
    def get_all(self) -> List[Tuple[int, str, str]]:
        return self._players.copy()
    
    def get_or_create(self, full_name: str) -> Optional[int]:
        """Simulate creating a player."""
        # Check if exists
        for pid, vorname, nachname in self._players:
            if f"{vorname} {nachname}" == full_name:
                return pid
        
        # Create new
        name_parts = full_name.strip().split(' ', 1)
        vorname = name_parts[0] if name_parts else full_name
        nachname = name_parts[1] if len(name_parts) > 1 else ""
        
        new_id = self._next_id
        self._players.append((new_id, vorname, nachname))
        self._next_id += 1
        
        print(f"💾 Dummy: Created player {full_name}")
        return new_id


class DummyMatchRepository:
    """Fake match repository for offline mode."""

    def __init__(self) -> None:
        self._matches: List[Tuple] = []
        self._set_scores: dict = {}

    def save(
        self,
        player1_id: int,
        player2_id: int,
        sets_player1: int,
        sets_player2: int,
        tournament_id: Optional[int] = None,
        set_scores: Optional[List[Tuple[int, int]]] = None,
    ) -> Optional[int]:
        match_id = len(self._matches) + 1
        print(f"💾 Dummy: Saved match {sets_player1}-{sets_player2} (ID: {match_id})")
        self._matches.append((
            match_id, player1_id, player2_id,
            sets_player1, sets_player2, tournament_id, datetime.now()
        ))
        if set_scores:
            self._set_scores[match_id] = set_scores
        return match_id

    def get_by_tournament(self, tournament_id: int) -> List[Tuple]:
        print(f"💾 Dummy: Loading matches for tournament {tournament_id}")
        return []

    def get_set_scores(self, match_id: int) -> List[Tuple[int, int, int]]:
        scores = self._set_scores.get(match_id, [])
        return [(i + 1, p1, p2) for i, (p1, p2) in enumerate(scores)]


class DummyTournamentRepository:
    """Fake tournament repository for offline mode."""
    
    def __init__(self) -> None:
        self._tournaments = [
            (1, "Test Turnier", datetime.now(), 3),
        ]
        self._next_id = 2
    
    def get_all(self) -> List[Tuple[int, str, datetime, int]]:
        return self._tournaments.copy()
    
    def create(self, name: str, sets_to_win: int = 3) -> Optional[int]:
        new_id = self._next_id
        self._tournaments.append((new_id, name, datetime.now(), sets_to_win))
        self._next_id += 1
        print(f"💾 Dummy: Created tournament {name}")
        return new_id
    
    def get_rankings(self, tournament_id: int) -> List[Tuple]:
        print(f"💾 Dummy: Loading rankings for tournament {tournament_id}")
        return [
            ("Max Mustermann", 5, 2, 12, 7, 5),
            ("Anna Schmidt", 4, 3, 10, 9, 1),
        ]


# ============================================================================
# Factory Function
# ============================================================================

def create_repositories(
    db: Optional[DatabaseConnection] = None,
    use_dummy: bool = False
) -> Tuple[PlayerRepository, MatchRepository, TournamentRepository]:
    """Create repository instances.
    
    Args:
        db: Database connection (None = create new)
        use_dummy: Force use of dummy repositories
    
    Returns:
        Tuple of (player_repo, match_repo, tournament_repo)
    """
    if use_dummy or db is None or not db.is_connected():
        print("💾 Using dummy repositories (offline mode)")
        return (
            DummyPlayerRepository(),
            DummyMatchRepository(),
            DummyTournamentRepository(),
        )
    
    return (
        MySQLPlayerRepository(db),
        MySQLMatchRepository(db),
        MySQLTournamentRepository(db),
    )
