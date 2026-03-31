# Legacy TTR GUI (Monolithic Version)

This file has been renamed from `ttr_gui.py` to `ttr_gui_legacy.py` as part of the Clean Architecture refactoring.

## DO NOT MODIFY THIS FILE

This is the original monolithic implementation kept for reference and fallback.

## New Architecture

The refactored version is being built in:
- `src/core/` - Business logic
- `src/database/` - Data access
- `src/ui/` - User interface components
- `src/main.py` - Application entry point

## Migration Status

✅ **Phase 1 Complete**: Core Architecture
- MatchEngine (pure Python business logic)
- Repository Pattern (database abstraction)
- Configuration Management (.env)
- Unit Tests

🚧 **Phase 2 In Progress**: UI Components
- ✅ Stylesheet extracted (styles.qss)
- ✅ Confetti widget extracted
- ✅ Custom dialogs extracted
- 🚧 Page components (Scoreboard, Setup, etc.)

## Running the Application

**Legacy version:**
```bash
python ttr_gui_legacy.py
```

**New version (temporary, uses legacy GUI):**
```bash
python src/main.py
```

---

**Original file location**: `c:\TTR_Project\ttr_gui.py`
**Renamed on**: 2026-02-05
**Refactoring started**: Phase 1 completed, Phase 2 in progress
