"""
Unit Tests for MatchEngine
===========================

Tests the core business logic without any UI dependencies.
Run with: pytest tests/test_match_engine.py -v
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.match_engine import MatchEngine
from core.constants import PLAYER_1, PLAYER_2


def test_match_initialization():
    """Test that a match initializes with correct defaults."""
    engine = MatchEngine(
        player1_name="Alice",
        player2_name="Bob",
        sets_to_win=3,
        initial_server=PLAYER_1
    )
    
    assert engine.score_player1 == 0
    assert engine.score_player2 == 0
    assert engine.sets_player1 == 0
    assert engine.sets_player2 == 0
    assert engine.server == PLAYER_1
    assert engine.sets_to_win == 3


def test_add_point_basic():
    """Test adding points to players."""
    engine = MatchEngine(sets_to_win=1)
    
    result = engine.add_point(PLAYER_1)
    assert engine.score_player1 == 1
    assert engine.score_player2 == 0
    assert not result.set_won
    assert not result.match_won
    
    result = engine.add_point(PLAYER_2)
    assert engine.score_player1 == 1
    assert engine.score_player2 == 1


def test_set_win_normal():
    """Test set win with 11:0 score."""
    engine = MatchEngine(sets_to_win=3)
    
    # Player 1 scores 11 points
    for _ in range(11):
        result = engine.add_point(PLAYER_1)
    
    # Last point should win the set
    assert result.set_won
    assert result.winner == PLAYER_1
    assert not result.match_won
    assert engine.sets_player1 == 1
    assert engine.sets_player2 == 0


def test_set_win_deuce():
    """Test set win in deuce situation (11:11 -> 13:11)."""
    engine = MatchEngine(sets_to_win=3)
    
    # Score to 10:10
    for _ in range(10):
        engine.add_point(PLAYER_1)
        engine.add_point(PLAYER_2)
    
    assert engine.score_player1 == 10
    assert engine.score_player2 == 10
    
    # Player 1 scores two more
    result = engine.add_point(PLAYER_1)
    assert not result.set_won  # 11:10, need 2 point lead
    
    result = engine.add_point(PLAYER_1)
    assert result.set_won  # 12:10, 2 point lead
    assert result.winner == PLAYER_1


def test_match_win():
    """Test match win (Best of 5 = 3 sets)."""
    engine = MatchEngine(sets_to_win=3)
    
    # Player 1 wins 3 sets
    for set_num in range(3):
        for _ in range(11):
            result = engine.add_point(PLAYER_1)
        
        if set_num < 2:
            assert result.set_won
            assert not result.match_won
            engine.reset_set()
    
    # After 3rd set
    assert result.set_won
    assert result.match_won
    assert result.winner == PLAYER_1
    assert engine.is_match_finished()
    assert engine.get_winner() == PLAYER_1


def test_serve_change_normal():
    """Test serve changes every 2 points in normal play."""
    engine = MatchEngine(initial_server=PLAYER_1)
    
    assert engine.server == PLAYER_1
    
    engine.add_point(PLAYER_1)
    assert engine.server == PLAYER_1  # Still player 1
    
    engine.add_point(PLAYER_1)
    assert engine.server == PLAYER_2  # Changed after 2 points
    
    engine.add_point(PLAYER_2)
    assert engine.server == PLAYER_2
    
    engine.add_point(PLAYER_2)
    assert engine.server == PLAYER_1  # Changed again


def test_serve_change_deuce():
    """Test serve changes every point in deuce (10:10+)."""
    engine = MatchEngine(initial_server=PLAYER_1)
    
    # Score to 10:10
    for _ in range(10):
        engine.add_point(PLAYER_1)
        engine.add_point(PLAYER_2)
    
    current_server = engine.server
    
    # In deuce, serve changes every point
    engine.add_point(PLAYER_1)
    assert engine.server != current_server
    
    current_server = engine.server
    engine.add_point(PLAYER_2)
    assert engine.server != current_server


def test_undo_point():
    """Test undo functionality."""
    engine = MatchEngine(sets_to_win=1)
    
    # Add some points
    engine.add_point(PLAYER_1)
    engine.add_point(PLAYER_1)
    engine.add_point(PLAYER_2)
    
    assert engine.score_player1 == 2
    assert engine.score_player2 == 1
    
    # Undo last point
    success = engine.undo_last_point()
    assert success
    assert engine.score_player1 == 2
    assert engine.score_player2 == 0
    
    # Undo again
    success = engine.undo_last_point()
    assert success
    assert engine.score_player1 == 1
    
    # Can undo multiple times
    success = engine.undo_last_point()
    assert success
    assert engine.score_player1 == 0
    
    # No more history
    success = engine.undo_last_point()
    assert not success


def test_undo_set_win():
    """Test undo after set win."""
    engine = MatchEngine(sets_to_win=3)
    
    # Player 1 wins set 11:0
    for _ in range(11):
        result = engine.add_point(PLAYER_1)
    
    assert result.set_won
    assert engine.sets_player1 == 1
    
    # Undo the winning point
    engine.undo_last_point()
    assert engine.score_player1 == 10
    assert engine.sets_player1 == 0  # Set win was undone


def test_invalid_player():
    """Test that invalid player numbers raise ValueError."""
    engine = MatchEngine()
    
    try:
        engine.add_point(3)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "must be 1 or 2" in str(e)


def test_invalid_sets_to_win():
    """Test that invalid sets_to_win raises ValueError."""
    try:
        MatchEngine(sets_to_win=0)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "at least 1" in str(e)


if __name__ == "__main__":
    # Run tests manually
    print("Running MatchEngine tests...")
    
    tests = [
        test_match_initialization,
        test_add_point_basic,
        test_set_win_normal,
        test_set_win_deuce,
        test_match_win,
        test_serve_change_normal,
        test_serve_change_deuce,
        test_undo_point,
        test_undo_set_win,
        test_invalid_player,
        test_invalid_sets_to_win,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: Unexpected error: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*50}")
