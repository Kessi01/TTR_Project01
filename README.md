# TTR - Table Tennis Referee ✨

Ein professionelles Tischtennis-Scoreboard mit Clean Architecture.

## 🏗️ Projektstruktur

```
TTR_Project/
├── src/
│   ├── core/              # Pure Python Business Logic (NO PyQt6!)
│   │   ├── constants.py   # Enums & Konstanten statt Magic Numbers
│   │   ├── models.py      # Datenmodelle (Player, Match, etc.)
│   │   └── match_engine.py # Spielregeln & Punktestand
│   │
│   ├── database/          # Datenbank-Schicht
│   │   ├── connection.py  # Verbindungsmanagement mit Retry-Logik
│   │   └── repository.py  # Repository Pattern (MySQL & Dummy)
│   │
│   ├── ui/                # PyQt6 Views & Components
│   │   ├── pages/         # Vollbild-Seiten
│   │   ├── widgets/       # Wiederverwendbare Widgets
│   │   └── resources/     # Stylesheets, Assets
│   │
│   └── config.py          # Konfiguration via Umgebungsvariablen
│
├── tests/                 # Unit & Integration Tests
│   └── test_match_engine.py
│
├── .env                   # Lokale Konfiguration (NICHT in Git!)
├── .env.example          # Template für Konfiguration
├── requirements.txt      # Python-Dependencies
└── README.md             # Diese Datei
```

## 🚀 Installation

### 1. Python-Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### 2. Konfiguration einrichten

Kopiere `.env.example` zu `.env` und passe die Datenbank-Zugangsdaten an:

```bash
cp .env.example .env
```

Bearbeite `.env`:

```env
DB_HOST=localhost
DB_NAME=ttr_db
DB_USER=root
DB_PASSWORD=dein_sicheres_passwort  # <-- HIER ANPASSEN!
```

### 3. Datenbank-Schema

Die Anwendung erwartet folgende Tabellen:
- `spieler` (id, vorname, nachname)
- `matches` (id, spieler1_id, spieler2_id, satz_score_s1, satz_score_s2, turnier_id, datum)
- `turniere` (id, name, erstellt_am, sets_to_win)

## ⚙️ Konfiguration

Alle Konfigurationen werden über Umgebungsvariablen gesteuert (`.env`-Datei):

### Datenbank
- `DB_HOST`: Host (default: localhost)
- `DB_PORT`: Port (default: 3306)
- `DB_NAME`: Datenbankname (default: ttr_db)
- `DB_USER`: Benutzer (default: root)
- `DB_PASSWORD`: **ERFORDERLICH!** Dein DB-Passwort
- `DB_AUTH_PLUGIN`: Auth-Plugin (default: mysql_native_password)

### Anwendung
- `APP_FULLSCREEN`: Vollbild-Modus (default: true)
- `APP_DEBUG`: Debug-Modus (default: false)
- `APP_KIOSK_MODE`: Kiosk-Modus (default: false)

## 🧪 Tests ausführen

### Alle Tests

```bash
pytest tests/ -v
```

### Nur MatchEngine Tests

```bash
python tests/test_match_engine.py
```

## 🎯 Features

### ✅ Bereits implementiert (Phase 1)

- **Clean Architecture**: Strikte Trennung von Business Logic, UI und Database
- **MatchEngine**: Pure Python Spiellogik (vollständig testbar!)
  - Punktestand & Satzstand
  - Offizielle Tischtennis-Regeln (Aufschlagwechsel, Deuce, etc.)
  - Undo-Funktion
  - History-Tracking
- **Repository Pattern**: Abstraktion der Datenbankzugriffe
  - MySQL-Implementierung
  - Dummy-Implementierung (Offline-Modus!)
- **Configuration Management**: Umgebungsvariablen statt Hardcoded Secrets
- **Umfassende Tests**: Unit Tests für MatchEngine
- **Type Hints & Docstrings**: Sauberer, dokumentierter Code

### 🚧 In Arbeit (Phase 2)

- UI-Komponenten extrahieren
- Externes Stylesheet (`.qss`-Datei)
- Modulare Widgets & Dialoge

## 📚 Architektur-Prinzipien

### Separation of Concerns

1. **Core Layer** (`src/core/`)
   - **KEINE** PyQt6-Imports!
   - Pure Python Business Logic
   - Vollständig testbar ohne UI

2. **Database Layer** (`src/database/`)
   - Abstraktion via Protocol (Interface)
   - Dependency Injection für Testbarkeit
   - Graceful Degradation (Offline-Modus bei DB-Ausfall)

3. **UI Layer** (`src/ui/`)
   - Nur Darstellung & User-Events
   - Delegiert an MatchEngine für Logik
   - Signal/Slot für Kommunikation

### Design Patterns

- **Repository Pattern**: Datenbank-Zugriffe abstrahiert
- **Dependency Injection**: Testbare Komponenten
- **Observer Pattern**: Qt Signals/Slots
- **MVC/MVVM**: Trennung von Model, View, Controller

## 🔒 Sicherheit

- ✅ **Keine Hardcoded Passwörter** mehr im Code
- ✅ `.env` in `.gitignore` (wird NICHT committed)
- ✅ `.env.example` als Template
- ✅ Sichere Konfiguration via Umgebungsvariablen

## 🐛 Troubleshooting

### "DB_PASSWORD is empty!"

Lösung: Setze `DB_PASSWORD` in deiner `.env`-Datei:

```env
DB_PASSWORD=dein_passwort_hier
```

### "mysql-connector-python nicht installiert"

Lösung: Installiere alle Dependencies:

```bash
pip install -r requirements.txt
```

### Offline-Modus

Wenn keine Datenbank verfügbar ist, läuft die App im **Offline-Modus** mit Dummy-Daten.
Du siehst dann: `💾 Using dummy repositories (offline mode)`

## 🧑‍💻 Entwicklung

### Code-Qualität

- **Type Hints** (PEP 484): Alle Funktionen haben Type Annotations
- **Docstrings** (Google Style): Klassen & Methoden dokumentiert
- **PEP 8**: Code-Style konform
- **Keine Magic Numbers**: Alles durch Konstanten/Enums ersetzt

### Tests schreiben

Beispiel für einen MatchEngine-Test:

```python
from src.core.match_engine import MatchEngine
from src.core.constants import PLAYER_1

def test_point_scoring():
    engine = MatchEngine(sets_to_win=3)
    result = engine.add_point(PLAYER_1)
    
    assert engine.score_player1 == 1
    assert not result.set_won
```

## 📄 Lizenz

Internes Projekt - Florian Kessi

## 🙏 Danksagung

Refactoring durchgeführt von Google Deepmind's Antigravity AI Coding Assistant.
