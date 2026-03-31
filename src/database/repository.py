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
        tournament_id: Optional[int] = None
    ) -> bool:
        """Save a completed match.
        
        Returns:
            True if successful
        """
        ...
    
    def get_by_tournament(self, tournament_id: int) -> List[Tuple]:
        """Get all matches for a tournament.
        
        Returns:
            List of (match_id, player1_name, player2_name, score1, score2, date)
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
        tournament_id: Optional[int] = None
    ) -> bool:
        """Save match to database."""
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
            cursor.close()
            
            print(f"✅ Match saved: {sets_player1}-{sets_player2}")
            return True
            
        except Error as e:
            print(f"❌ Error saving match: {e}")
            self.db.rollback()
            return False
    
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
    
    def get_rankings(self, tournament_id: int) -> List[Tuple[str, int, int]]:
        """Get player rankings for a tournament."""
        try:
            cursor = self.db.get_cursor()
            query = """
                SELECT name, wins, losses FROM (
                    SELECT
                        CONCAT(s.vorname, ' ', s.nachname) as name,
                        SUM(CASE
                            WHEN (m.spieler1_id = s.id AND m.satz_score_s1 > m.satz_score_s2)
                              OR (m.spieler2_id = s.id AND m.satz_score_s2 > m.satz_score_s1)
                            THEN 1 ELSE 0 END) as wins,
                        SUM(CASE
                            WHEN (m.spieler1_id = s.id AND m.satz_score_s1 < m.satz_score_s2)
                              OR (m.spieler2_id = s.id AND m.satz_score_s2 < m.satz_score_s1)
                            THEN 1 ELSE 0 END) as losses
                    FROM spieler s
                    JOIN matches m ON s.id = m.spieler1_id OR s.id = m.spieler2_id
                    WHERE m.turnier_id = %s
                    GROUP BY s.id, s.vorname, s.nachname
                ) as stats
                ORDER BY wins DESC, losses ASC
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
    
    def save(
        self,
        player1_id: int,
        player2_id: int,
        sets_player1: int,
        sets_player2: int,
        tournament_id: Optional[int] = None
    ) -> bool:
        print(f"💾 Dummy: Saved match {sets_player1}-{sets_player2}")
        self._matches.append((
            len(self._matches) + 1,
            player1_id,
            player2_id,
            sets_player1,
            sets_player2,
            tournament_id,
            datetime.now()
        ))
        return True
    
    def get_by_tournament(self, tournament_id: int) -> List[Tuple]:
        print(f"💾 Dummy: Loading matches for tournament {tournament_id}")
        return []


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
    
    def get_rankings(self, tournament_id: int) -> List[Tuple[str, int, int]]:
        print(f"💾 Dummy: Loading rankings for tournament {tournament_id}")
        return [
            ("Max Mustermann", 5, 2),
            ("Anna Schmidt", 4, 3),
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
