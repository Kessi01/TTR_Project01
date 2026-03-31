"""
TTR - Table Tennis Referee GUI
Touch-optimiertes Scoreboard für Raspberry Pi
FEATURES:
- Fullscreen (Kiosk Mode)
- Auto-Complete für Spielernamen
- Rahmenlose Dialog-Boxen (Custom Design)
- Datenbank-Anbindung
"""

import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QLineEdit, QFrame, QMessageBox,
    QSizePolicy, QSpacerItem, QListWidget, QListWidgetItem, QTableWidget,
    QTableWidgetItem, QHeaderView, QInputDialog, QAbstractItemView,
    QComboBox, QRadioButton, QButtonGroup, QCompleter
)
from PyQt6.QtCore import Qt, QSize, QTimer, QRectF
from PyQt6.QtGui import QFont, QColor, QPalette, QPixmap, QPainter, QBrush
import os

try:
    import mysql.connector
    from mysql.connector import Error
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("⚠️ mysql.connector nicht installiert. Nutze Dummy-Daten.")


# ==================== DATENBANK-KONFIGURATION ====================
DB_CONFIG = {
    'host': 'localhost',
    'database': 'ttr_db',
    'user': 'root',
    'password': 'Pat@3400Roy',  # Ihr Passwort
    'auth_plugin': 'mysql_native_password'
}


# ==================== STYLESHEET (Globales Dark Theme) ====================
DARK_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #1a1a2e;
    color: #ffffff;
}

QLabel {
    color: #ffffff;
    font-family: 'Segoe UI', Arial, sans-serif;
}

QPushButton {
    background-color: #16213e;
    color: #ffffff;
    border: 2px solid #0f3460;
    border-radius: 15px;
    padding: 20px;
    font-size: 22px;
    font-weight: bold;
    font-family: 'Segoe UI', Arial, sans-serif;
    min-height: 60px;
}

QPushButton:hover {
    background-color: #0f3460;
    border-color: #00d9ff;
}

QPushButton:pressed {
    background-color: #00d9ff;
    color: #1a1a2e;
}

QPushButton#primary {
    background-color: #00d9ff;
    color: #1a1a2e;
    border: none;
}

QPushButton#primary:hover {
    background-color: #00b8d4;
}

QPushButton#danger {
    background-color: #e94560;
    border-color: #e94560;
}

QPushButton#danger:hover {
    background-color: #c73e54;
}

QPushButton#score {
    background-color: #0f3460;
    border: 3px solid #00d9ff;
    border-radius: 20px;
    font-size: 48px;
    min-width: 120px;
    min-height: 120px;
}

QPushButton#score:pressed {
    background-color: #00d9ff;
    color: #1a1a2e;
}

QLineEdit {
    background-color: #16213e;
    color: #ffffff;
    border: 2px solid #0f3460;
    border-radius: 10px;
    padding: 15px;
    font-size: 22px;
    min-height: 50px;
}

QLineEdit:focus {
    border-color: #00d9ff;
}

QLineEdit::placeholder {
    color: #666666;
}

QFrame#separator {
    background-color: #0f3460;
    max-height: 2px;
}

QLabel#title {
    color: #00d9ff;
    font-size: 48px;
    font-weight: bold;
}

QLabel#subtitle {
    color: #888888;
    font-size: 18px;
}

QLabel#scoreBig {
    color: #ffffff;
    font-size: 540px;
    font-weight: bold;
}

QLabel#playerName {
    color: #00d9ff;
    font-size: 48px;
    font-weight: bold;
}

QLabel#setScore {
    color: #ffffff;
    font-size: 108px;
    font-weight: bold;
}

QLabel#setLabel {
    color: #888888;
    font-size: 24px;
}
"""

# ==================== HILFSFUNKTION FÜR RAHMENLOSE POPUPS ====================
def show_custom_confirm_dialog(parent, title, text):
    """Zeigt ein rahmenloses Bestätigungsfenster an (Style wie Info-Dialog).
       Returns: True bei Ja, False bei Nein.
    """
    from PyQt6.QtWidgets import QDialog, QLayout
    
    dialog = QDialog(parent)
    dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
    
    # Layout erstellen
    layout = QVBoxLayout(dialog)
    # WICHTIG: Dialog passt sich automatisch dem Inhalt an
    layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
    layout.setSpacing(20)
    layout.setContentsMargins(30, 30, 30, 40)
    
    # Style setzen
    dialog.setStyleSheet("""
        QDialog {
            background-color: #1a1a2e;
            border: 3px solid #00d9ff;
            border-radius: 15px;
        }
    """)
    
    # Text Label
    lbl_text = QLabel(text)
    lbl_text.setStyleSheet("""
        color: white;
        font-size: 22px;
        font-weight: bold;
        background: transparent;
        border: none;
    """)
    lbl_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl_text.setWordWrap(True)
    layout.addWidget(lbl_text)
    
    # Button Layout
    btn_layout = QHBoxLayout()
    btn_layout.setSpacing(20)
    btn_layout.setContentsMargins(10, 10, 10, 10)
    
    # Ja Button (Blau)
    btn_yes = QPushButton("Ja")
    btn_yes.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_yes.setStyleSheet("""
        QPushButton {
            background-color: #16213e;
            color: white;
            border: 3px solid #00d9ff;
            border-radius: 10px;
            font-size: 22px;
            font-weight: bold;
            min-width: 140px;
            min-height: 60px;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #00d9ff;
            color: #1a1a2e;
        }
    """)
    btn_yes.clicked.connect(dialog.accept)
    btn_layout.addWidget(btn_yes)
    
    # Nein Button (Rot)
    btn_no = QPushButton("Nein")
    btn_no.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_no.setStyleSheet("""
        QPushButton {
            background-color: #16213e;
            color: white;
            border: 3px solid #e94560;
            border-radius: 10px;
            font-size: 22px;
            font-weight: bold;
            min-width: 140px;
            min-height: 60px;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #e94560;
        }
    """)
    btn_no.clicked.connect(dialog.reject)
    btn_layout.addWidget(btn_no)
    
    # Buttons zentriert ins Layout
    wrapper_widget = QWidget()
    wrapper_widget.setLayout(btn_layout)
    wrapper_widget.setStyleSheet("background: transparent; border: none;")
    layout.addWidget(wrapper_widget, 0, Qt.AlignmentFlag.AlignCenter)
    
    return dialog.exec() == QDialog.DialogCode.Accepted


def show_custom_info_dialog(parent, title, text, cancel_text=None):
    """Zeigt ein rahmenloses Info-Fenster mit zentriertem OK-Button an.
       Optional kann ein Abbrechen-Button hinzugefügt werden.
       Returns: True bei OK, False bei Abbrechen.
    """
    from PyQt6.QtWidgets import QDialog, QLayout
    
    dialog = QDialog(parent)
    dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
    
    # Layout erstellen
    layout = QVBoxLayout(dialog)
    # WICHTIG: Dialog passt sich automatisch dem Inhalt an
    layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
    layout.setSpacing(20)
    layout.setContentsMargins(30, 30, 30, 40)
    
    # Style setzen - Identisch zu show_custom_confirm_dialog
    dialog.setStyleSheet("""
        QDialog {
            background-color: #1a1a2e;
            border: 3px solid #00d9ff;
            border-radius: 15px;
        }
        QPushButton {
            background-color: #16213e;
            color: white;
            border: 2px solid #0f3460;
            border-radius: 10px;
            font-size: 22px;
            font-weight: bold;
            min-width: 140px;
            min-height: 60px;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #00d9ff;
            color: #1a1a2e;
            border-color: #00d9ff;
        }
    """)
    
    # Text Label
    lbl_text = QLabel(text)
    lbl_text.setStyleSheet("""
        color: white;
        font-size: 22px;
        font-weight: bold;
        background: transparent;
        border: none;
    """)
    lbl_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl_text.setWordWrap(True)
    layout.addWidget(lbl_text)
    
    # Button Layout
    btn_layout = QHBoxLayout()
    btn_layout.setSpacing(20)
    btn_layout.setContentsMargins(10, 10, 10, 10) # Puffer für Rahmen
    
    # OK Button
    btn_ok = QPushButton("OK")
    btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
    # OK Button bekommt blauen Rahmen
    btn_ok.setStyleSheet("""
        QPushButton {
            background-color: #16213e;
            color: white;
            border: 3px solid #00d9ff;
            border-radius: 10px;
            font-size: 22px;
            font-weight: bold;
            min-width: 140px;
            min-height: 60px;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #00d9ff;
            color: #1a1a2e;
        }
    """)
    btn_ok.clicked.connect(dialog.accept)
    btn_layout.addWidget(btn_ok)
    
    # Optionaler Cancel Button
    if cancel_text:
        btn_cancel = QPushButton(cancel_text)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        # Cancel Button bekommt roten Rahmen
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #16213e;
                color: white;
                border: 3px solid #e94560;
                border-radius: 10px;
                font-size: 22px;
                font-weight: bold;
                min-width: 140px;
                min-height: 60px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #e94560;
            }
        """)
        btn_cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_cancel)
    
    # Buttons zentriert ins Layout
    wrapper_widget = QWidget()
    wrapper_widget.setLayout(btn_layout)
    # WICHTIG: Transparent background für Wrapper, sonst grauer Kasten
    wrapper_widget.setStyleSheet("background: transparent; border: none;")
    layout.addWidget(wrapper_widget, 0, Qt.AlignmentFlag.AlignCenter)
    
    return dialog.exec() == QDialog.DialogCode.Accepted


# ==================== KONFETTI-OVERLAY FÜR SATZGEWINN ====================
class ConfettiParticle:
    """Einzelnes Konfetti-Partikel für Explosionseffekt."""
    def __init__(self, x, y, color, angle):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(15, 30)
        
        # Geschwindigkeit basierend auf Winkel (Explosion nach außen)
        import math
        # Erhöhte Geschwindigkeit für stärkeren Explosionseffekt
        speed = random.uniform(25, 75)
        self.speed_x = math.cos(math.radians(angle)) * speed
        self.speed_y = math.sin(math.radians(angle)) * speed
        
        # Schwerkraft und Reibung
        self.gravity = 0.30  # Etwas leichter für längere Flugzeit
        self.friction = 0.96  # Luftreibung
        
        self.rotation = random.randint(0, 360)
        self.rotation_speed = random.uniform(-15, 15)
        self.life = 1.0  # Lebensdauer (1.0 = voll, 0.0 = tot)
        self.fade_speed = random.uniform(0.002, 0.006)  # Langsames Verblassen (lange Dauer)


class ConfettiOverlay(QWidget):
    """Transparentes Overlay das Konfetti-Explosion auf einer Seite zeigt."""
    
    def __init__(self, parent=None, side="left"):
        super().__init__(parent)
        self.side = side  # "left" oder "right"
        self.particles = []
        self.is_active = False
        self.explosion_done = False
        
        # Timer für Animation (schneller für flüssigere Bewegung)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_particles)
        
        # Transparenter Hintergrund
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")
        
        # Konfetti-Farben (festlich)
        self.colors = [
            QColor("#FFD700"),  # Gold
            QColor("#FF6B6B"),  # Rot
            QColor("#4ECDC4"),  # Türkis
            QColor("#45B7D1"),  # Hellblau
            QColor("#96E6A1"),  # Hellgrün
            QColor("#DDA0DD"),  # Lila
            QColor("#FF8C42"),  # Orange
            QColor("#00d9ff"),  # Cyan (passend zum Theme)
            QColor("#FFFFFF"),  # Weiß
        ]
    
    def start_confetti(self):
        """Startet die Konfetti-Explosion vom Zentrum."""
        self.is_active = True
        self.explosion_done = False
        self.particles = []
        
        # Sicherstellen dass Overlay die Grösse des Parents hat
        if self.parent():
            self.resize(self.parent().size())
        
        # Explosion vom Zentrum
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # NOCH MEHR Partikel (800) und volle 360 Grad
        for i in range(800):
            angle = random.uniform(0, 360)
            color = random.choice(self.colors)
            self.particles.append(ConfettiParticle(center_x, center_y, color, angle))
        
        self.show()
        self.raise_()
        self.timer.start(20)  # 50 FPS
    
    def stop_confetti(self):
        """Stoppt die Konfetti-Animation."""
        self.is_active = False
        self.timer.stop()
        self.particles = []
        self.hide()
    
    def update_particles(self):
        """Aktualisiert Partikel-Positionen."""
        if not self.is_active:
            return
        
        # Partikel bewegen
        for p in self.particles:
            # Bewegung mit Reibung
            p.x += p.speed_x
            p.y += p.speed_y
            
            # Schwerkraft anwenden
            p.speed_y += p.gravity
            
            # Reibung
            p.speed_x *= p.friction
            p.speed_y *= p.friction
            
            # Rotation
            p.rotation += p.rotation_speed
            
            # Verblassen
            p.life -= p.fade_speed
        
        # Tote Partikel entfernen
        self.particles = [p for p in self.particles if p.life > 0]
        
        self.update()
    
    def paintEvent(self, event):
        """Zeichnet die Konfetti-Partikel."""
        if not self.is_active or not self.particles:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        for p in self.particles:
            painter.save()
            painter.translate(p.x, p.y)
            painter.rotate(p.rotation)
            
            # Farbe mit Transparenz basierend auf Lebensdauer
            color = QColor(p.color)
            color.setAlphaF(p.life)
            
            brush = QBrush(color)
            painter.setBrush(brush)
            painter.setPen(Qt.PenStyle.NoPen)
            
            # Rechteckiges Konfetti
            painter.drawRect(int(-p.size/2), int(-p.size/4), p.size, int(p.size/2))
            
            painter.restore()
    
    def mousePressEvent(self, event):
        """Klick stoppt die Animation."""
        self.stop_confetti()
        event.accept()


# ==================== VOLLBILD TOUCH-TASTATUR ====================
class FullscreenKeyboardPage(QWidget):
    """Vollbild Touch-Tastatur Seite."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.target_field = None  # Welches Feld wird bearbeitet
        self.callback = None  # Callback nach Eingabe
        self.shift_active = False
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet("background-color: #1a1a2e;")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ===== Oben: Titel zentriert =====
        top_layout = QHBoxLayout()
        
        # Platzhalter links für Symmetrie
        spacer_left = QWidget()
        spacer_left.setFixedWidth(60)
        top_layout.addWidget(spacer_left)
        
        # Titel in der Mitte
        self.title_label = QLabel("Eingabe")
        self.title_label.setStyleSheet("font-size: 28px; color: #00d9ff; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(self.title_label, 1)
        
        # Platzhalter rechts für Symmetrie
        spacer_right = QWidget()
        spacer_right.setFixedWidth(60)
        top_layout.addWidget(spacer_right)
        
        layout.addLayout(top_layout)
        
        # ===== Mitte: Eingabefeld mit Dropdown =====
        layout.addStretch()
        
        input_row = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setMinimumHeight(80)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #16213e;
                color: white;
                border: 3px solid #00d9ff;
                border-radius: 15px;
                padding: 15px;
                font-size: 32px;
            }
        """)
        self.input_field.setReadOnly(True)
        input_row.addWidget(self.input_field)
        
        # Dropdown-Button für Vorschläge
        self.btn_dropdown = QPushButton("▼")
        self.btn_dropdown.setFixedSize(80, 80)
        self.btn_dropdown.setStyleSheet("""
            QPushButton {
                background-color: #00d9ff;
                color: #1a1a2e;
                border: none;
                border-radius: 15px;
                font-size: 28px;
                font-weight: bold;
            }
            QPushButton:pressed { background-color: #00b8d4; }
        """)
        self.btn_dropdown.clicked.connect(self.toggle_suggestions)
        input_row.addWidget(self.btn_dropdown)
        
        layout.addLayout(input_row)
        
        # Vorschlagsliste (zunächst versteckt)
        self.suggestions_list = QListWidget()
        self.suggestions_list.setMaximumHeight(200)
        self.suggestions_list.setStyleSheet("""
            QListWidget {
                background-color: #16213e;
                color: white;
                border: 2px solid #00d9ff;
                border-radius: 10px;
                font-size: 24px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #0f3460;
            }
            QListWidget::item:selected {
                background-color: #00d9ff;
                color: #1a1a2e;
            }
        """)
        self.suggestions_list.itemClicked.connect(self.on_suggestion_selected)
        self.suggestions_list.hide()
        layout.addWidget(self.suggestions_list)
        
        layout.addSpacing(20)
        
        # ===== Tastatur =====
        keyboard_widget = QWidget()
        keyboard_layout = QVBoxLayout(keyboard_widget)
        keyboard_layout.setSpacing(8)
        
        # Schweizer QWERTZ Layout
        rows = [
            ['Q', 'W', 'E', 'R', 'T', 'Z', 'U', 'I', 'O', 'P', 'Ü'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Ö', 'Ä'],
            ['⇧', 'Y', 'X', 'C', 'V', 'B', 'N', 'M', '⌫'],
            ['←', '___SPACE___', '✓']
        ]
        
        self.shift_btn = None  # Referenz für Farbwechsel
        self.letter_buttons = []  # Referenzen für Buchstaben-Tasten
        self.number_mode = False
        
        for row in rows:
            row_layout = QHBoxLayout()
            row_layout.setSpacing(6)
            
            for key in row:
                btn = QPushButton()
                btn.setMinimumHeight(65)
                
                if key == '___SPACE___':
                    btn.setText("")
                    btn.setMinimumWidth(600)
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #3a3a4a;
                            color: white;
                            border: none;
                            border-radius: 8px;
                        }
                        QPushButton:pressed { background-color: #5a5a6a; }
                    """)
                    actual_key = ' '
                elif key == '✓':
                    btn.setText("OK")
                    btn.setMinimumWidth(120)
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #00d9ff;
                            color: #1a1a2e;
                            border: none;
                            border-radius: 8px;
                            font-size: 18px;
                            font-weight: bold;
                        }
                        QPushButton:pressed { background-color: #00b8d4; }
                    """)
                    actual_key = key
                elif key == '⌫':
                    btn.setText("⌫")
                    btn.setMinimumWidth(70)
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #3a3a4a;
                            color: white;
                            border: none;
                            border-radius: 8px;
                            font-size: 24px;
                        }
                        QPushButton:pressed { background-color: #5a5a6a; }
                    """)
                    actual_key = key
                elif key == '⇧':
                    btn.setText("⇧")
                    btn.setMinimumWidth(55)
                    self.shift_btn = btn  # Speichere Referenz
                    self.update_shift_button_style()
                    actual_key = key
                elif key == '←':
                    btn.setText("←")
                    btn.setMinimumWidth(55)
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #3a3a4a;
                            color: white;
                            border: none;
                            border-radius: 8px;
                            font-size: 20px;
                        }
                        QPushButton:pressed { background-color: #5a5a6a; }
                    """)
                    actual_key = '←'
                else:
                    btn.setText(key.lower())  # Standardmäßig klein
                    btn.setMinimumWidth(55)
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #4a4a5a;
                            color: white;
                            border: none;
                            border-radius: 8px;
                            font-size: 22px;
                            font-weight: bold;
                        }
                        QPushButton:pressed { background-color: #6a6a7a; }
                    """)
                    actual_key = key
                    self.letter_buttons.append((btn, key))  # Speichere Referenz
                
                btn.clicked.connect(lambda checked, k=actual_key: self.key_pressed(k))
                row_layout.addWidget(btn)
            
            keyboard_layout.addLayout(row_layout)
        
        layout.addWidget(keyboard_widget)
        layout.addStretch()
    
    def update_shift_button_style(self):
        """Aktualisiert Shift-Button Farbe basierend auf Status."""
        if self.shift_btn:
            if self.shift_active:
                self.shift_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #00d9ff;
                        color: #1a1a2e;
                        border: none;
                        border-radius: 8px;
                        font-size: 24px;
                    }
                """)
            else:
                self.shift_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3a3a4a;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-size: 24px;
                    }
                    QPushButton:pressed { background-color: #5a5a6a; }
                """)
        
        # Buchstaben groß/klein aktualisieren
        for btn, key in self.letter_buttons:
            if self.shift_active:
                btn.setText(key.upper())
            else:
                btn.setText(key.lower())
    
    def key_pressed(self, key):
        """Verarbeitet Tastendruck."""
        current = self.input_field.text()
        
        if key == '⌫':
            self.input_field.setText(current[:-1])
        elif key == '⇧':
            self.shift_active = not self.shift_active
            self.update_shift_button_style()
        elif key == '✓':
            self.on_confirm()
        elif key == ' ':
            self.input_field.setText(current + ' ')
        elif key == '←':
            self.on_exit()  # Zurück ohne zu speichern
        else:
            char = key.lower() if not self.shift_active else key.upper()
            self.input_field.setText(current + char)
            if self.shift_active:
                self.shift_active = False
                self.update_shift_button_style()
    
    def open_for_field(self, target_line_edit, callback, title="Eingabe"):
        """Öffnet Tastatur für ein bestimmtes Feld."""
        self.target_field = target_line_edit
        self.callback = callback
        self.input_field.setText(target_line_edit.text())
        self.shift_active = False
        self.suggestions_list.hide()
        self.title_label.setText(title)
        self.load_suggestions()
    
    def load_suggestions(self):
        """Lädt Spielervorschläge aus der Datenbank."""
        self.all_suggestions = []
        if self.main_window and self.main_window.db:
            spieler = self.main_window.db.get_spieler()
            self.all_suggestions = [f"{s[1]} {s[2]}" for s in spieler]
    
    def toggle_suggestions(self):
        """Zeigt/versteckt die Vorschlagsliste."""
        if self.suggestions_list.isVisible():
            self.suggestions_list.hide()
        else:
            self.update_suggestions()
            self.suggestions_list.show()
    
    def update_suggestions(self):
        """Aktualisiert die Vorschlagsliste basierend auf der Eingabe."""
        self.suggestions_list.clear()
        current_text = self.input_field.text().lower()
        
        for name in self.all_suggestions:
            if name.lower().startswith(current_text) or current_text == "":
                self.suggestions_list.addItem(name)
    
    def on_suggestion_selected(self, item):
        """Übernimmt den ausgewählten Vorschlag."""
        self.input_field.setText(item.text())
        self.suggestions_list.hide()
    
    def on_confirm(self):
        """Bestätigt Eingabe und kehrt zurück."""
        if self.target_field:
            self.target_field.setText(self.input_field.text())
        if self.callback:
            self.callback()
    
    def on_exit(self):
        """Beenden ohne Speichern."""
        if self.callback:
            self.callback()


class TouchInputDialog(QWidget):
    """Dialog mit Touch-Tastatur für Texteingabe."""
    
    def __init__(self, parent, title, label):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.result_text = ""
        self.accepted = False
        self.setup_ui(title, label)
    
    def setup_ui(self, title, label):
        self.setStyleSheet("""
            TouchInputDialog {
                background-color: #1a1a2e;
                border: 3px solid #00d9ff;
                border-radius: 15px;
            }
        """)
        self.setMinimumSize(600, 450)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titel
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 26px; color: #00d9ff; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Label
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 20px; color: white;")
        layout.addWidget(lbl)
        
        # Eingabefeld
        self.input_field = QLineEdit()
        self.input_field.setMinimumHeight(50)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #16213e;
                color: white;
                border: 2px solid #0f3460;
                border-radius: 10px;
                padding: 10px;
                font-size: 20px;
            }
        """)
        layout.addWidget(self.input_field)
        
        # Touch-Tastatur
        self.keyboard = TouchKeyboard(self)
        self.keyboard.set_target(self.input_field)
        self.keyboard.show()  # Immer sichtbar im Dialog
        layout.addWidget(self.keyboard)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        btn_cancel = QPushButton("Abbrechen")
        btn_cancel.setMinimumHeight(50)
        btn_cancel.setStyleSheet("""
            QPushButton { background-color: #16213e; color: white; border: 2px solid #e94560; border-radius: 10px; font-size: 18px; }
            QPushButton:pressed { background-color: #e94560; }
        """)
        btn_cancel.clicked.connect(self.on_cancel)
        btn_layout.addWidget(btn_cancel)
        
        btn_ok = QPushButton("OK")
        btn_ok.setMinimumHeight(50)
        btn_ok.setStyleSheet("""
            QPushButton { background-color: #00d9ff; color: #1a1a2e; border: none; border-radius: 10px; font-size: 18px; font-weight: bold; }
            QPushButton:pressed { background-color: #00b8d4; }
        """)
        btn_ok.clicked.connect(self.on_ok)
        btn_layout.addWidget(btn_ok)
        
        layout.addLayout(btn_layout)
    
    def on_ok(self):
        self.result_text = self.input_field.text()
        self.accepted = True
        self.close()
    
    def on_cancel(self):
        self.result_text = ""
        self.accepted = False
        self.close()
    
    @staticmethod
    def get_text(parent, title, label):
        """Zeigt den Dialog und gibt (text, ok) zurück."""
        dialog = TouchInputDialog(parent, title, label)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        # Dialog zentrieren
        if parent:
            parent_rect = parent.window().geometry()
            dialog.move(
                parent_rect.center().x() - dialog.width() // 2,
                parent_rect.center().y() - dialog.height() // 2
            )
        
        dialog.show()
        
        # Event-Loop bis Dialog geschlossen
        from PyQt6.QtCore import QEventLoop
        loop = QEventLoop()
        dialog.destroyed.connect(loop.quit)
        
        # Workaround: Warten auf Schließen
        while dialog.isVisible():
            QApplication.processEvents()
        
        return dialog.result_text, dialog.accepted


# ==================== DATENBANKVERBINDUNG ====================
class DatabaseManager:
    """Verwaltet alle Datenbankoperationen."""
    
    def __init__(self):
        self.connection = None
    
    def connect(self):
        """Stellt Verbindung zur Datenbank her."""
        if not MYSQL_AVAILABLE:
            return False
        
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                print("✅ Datenbankverbindung hergestellt.")
                return True
        except Error as e:
            print(f"❌ Datenbankfehler: {e}")
            return False
        return False
    
    def disconnect(self):
        """Schließt die Datenbankverbindung."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔌 Datenbankverbindung geschlossen.")
    
    def get_spieler(self):
        """Lädt alle Spieler aus der Datenbank."""
        spieler_liste = []
        
        if not MYSQL_AVAILABLE or not self.connection:
            # Dummy-Daten
            return [(1, "Max", "Mustermann"), (2, "Anna", "Schmidt")]
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id, vorname, nachname FROM spieler ORDER BY vorname, nachname")
            spieler_liste = cursor.fetchall()
            cursor.close()
        except Error as e:
            print(f"❌ Fehler beim Laden der Spieler: {e}")
        
        return spieler_liste
    
    def save_match(self, spieler1_id, spieler2_id, satz_score_s1, satz_score_s2, turnier_id=None):
        """Speichert ein Match-Ergebnis in der Datenbank."""
        if not MYSQL_AVAILABLE or not self.connection:
            print(f"💾 Match gespeichert (Dummy): {spieler1_id} vs {spieler2_id}")
            return True
        
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO matches (spieler1_id, spieler2_id, satz_score_s1, satz_score_s2, turnier_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (spieler1_id, spieler2_id, satz_score_s1, satz_score_s2, turnier_id))
            self.connection.commit()
            cursor.close()
            print(f"✅ Match gespeichert.")
            return True
        except Error as e:
            print(f"❌ Fehler beim Speichern des Matches: {e}")
            return False
    
    def get_or_create_spieler(self, name):
        """Sucht Spieler oder erstellt neu."""
        if not MYSQL_AVAILABLE or not self.connection:
            return 1 # Dummy ID
        
        name_parts = name.strip().split(' ', 1)
        vorname = name_parts[0] if name_parts else name
        nachname = name_parts[1] if len(name_parts) > 1 else ""
        
        try:
            cursor = self.connection.cursor()
            # Prüfen ob existiert
            query_select = "SELECT id FROM spieler WHERE vorname = %s AND nachname = %s"
            cursor.execute(query_select, (vorname, nachname))
            result = cursor.fetchone()
            
            if result:
                cursor.close()
                return result[0]
            
            # Neu anlegen
            query_insert = "INSERT INTO spieler (vorname, nachname) VALUES (%s, %s)"
            cursor.execute(query_insert, (vorname, nachname))
            self.connection.commit()
            spieler_id = cursor.lastrowid
            cursor.close()
            print(f"✅ Neuer Spieler angelegt: {name}")
            return spieler_id
            
        except Error as e:
            print(f"❌ Fehler bei Spieler-Verarbeitung: {e}")
            return None
    
    def save_match_with_names(self, spieler1_name, spieler2_name, satz_score_s1, satz_score_s2, turnier_id=None):
        spieler1_id = self.get_or_create_spieler(spieler1_name)
        spieler2_id = self.get_or_create_spieler(spieler2_name)
        
        if spieler1_id is None or spieler2_id is None:
            return False
        
        return self.save_match(spieler1_id, spieler2_id, satz_score_s1, satz_score_s2, turnier_id)
    
    # ==================== TURNIER-METHODEN ====================
    def get_turniere(self):
        if not MYSQL_AVAILABLE or not self.connection:
            return []
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id, name, erstellt_am FROM turniere ORDER BY erstellt_am DESC")
            turniere = cursor.fetchall()
            cursor.close()
            return turniere
        except Error as e:
            print(f"❌ Fehler beim Laden der Turniere: {e}")
            return []
    
    def create_turnier(self, name):
        if not MYSQL_AVAILABLE or not self.connection:
            return 1
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO turniere (name) VALUES (%s)", (name,))
            self.connection.commit()
            tid = cursor.lastrowid
            cursor.close()
            return tid
        except Error as e:
            print(f"❌ Fehler beim Erstellen des Turniers: {e}")
            return None
    
    def get_turnier_matches(self, turnier_id):
        if not MYSQL_AVAILABLE or not self.connection:
            return []
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT m.id, 
                       CONCAT(s1.vorname, ' ', s1.nachname) as spieler1,
                       CONCAT(s2.vorname, ' ', s2.nachname) as spieler2,
                       m.satz_score_s1, m.satz_score_s2, m.datum
                FROM matches m
                JOIN spieler s1 ON m.spieler1_id = s1.id
                JOIN spieler s2 ON m.spieler2_id = s2.id
                WHERE m.turnier_id = %s
                ORDER BY m.datum DESC
            """
            cursor.execute(query, (turnier_id,))
            matches = cursor.fetchall()
            cursor.close()
            return matches
        except Error as e:
            print(f"❌ Fehler beim Laden der Matches: {e}")
            return []
    
    def get_rangliste(self, turnier_id):
        if not MYSQL_AVAILABLE or not self.connection:
            return []
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT name, siege, niederlagen FROM (
                    SELECT 
                        CONCAT(s.vorname, ' ', s.nachname) as name,
                        SUM(CASE 
                            WHEN (m.spieler1_id = s.id AND m.satz_score_s1 > m.satz_score_s2) 
                              OR (m.spieler2_id = s.id AND m.satz_score_s2 > m.satz_score_s1) 
                            THEN 1 ELSE 0 END) as siege,
                        SUM(CASE 
                            WHEN (m.spieler1_id = s.id AND m.satz_score_s1 < m.satz_score_s2) 
                              OR (m.spieler2_id = s.id AND m.satz_score_s2 < m.satz_score_s1) 
                            THEN 1 ELSE 0 END) as niederlagen
                    FROM spieler s
                    JOIN matches m ON s.id = m.spieler1_id OR s.id = m.spieler2_id
                    WHERE m.turnier_id = %s
                    GROUP BY s.id, s.vorname, s.nachname
                ) as stats
                ORDER BY siege DESC, niederlagen ASC
            """
            cursor.execute(query, (turnier_id,))
            rangliste = cursor.fetchall()
            cursor.close()
            return rangliste
        except Error as e:
            print(f"❌ Fehler Rankliste: {e}")
            return []


# ==================== SEITE 1: STARTMENÜ ====================
class StartMenuPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)
        
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Logo / Titel
        logo_label = QLabel("TTR")
        logo_label.setObjectName("title")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
        
        subtitle = QLabel("Table Tennis Referee")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(separator)
        
        layout.addSpacing(40)
        
        btn_container = QWidget()
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setSpacing(20)
        
        btn_new_match = QPushButton("Neues Match")
        btn_new_match.setObjectName("primary")
        btn_new_match.setMinimumHeight(80)
        btn_new_match.clicked.connect(self.on_new_match)
        btn_layout.addWidget(btn_new_match)
        
        btn_turnier = QPushButton("Turnier")
        btn_turnier.setMinimumHeight(80)
        btn_turnier.clicked.connect(self.on_turnier)
        btn_layout.addWidget(btn_turnier)
        
        btn_exit = QPushButton("Beenden")
        btn_exit.setObjectName("danger")
        btn_exit.setMinimumHeight(80)
        btn_exit.clicked.connect(self.on_exit)
        btn_layout.addWidget(btn_exit)
        
        layout.addWidget(btn_container)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.setLayout(layout)
    
    def on_new_match(self):
        if self.main_window:
            self.main_window.show_match_setup()
    
    def on_turnier(self):
        if self.main_window:
            self.main_window.show_turnier_list()
    
    def on_exit(self):
        # HIER: Neues, rahmenloses Popup statt Standard-Dialog
        if show_custom_confirm_dialog(self, 'Beenden', 'Möchtest du TTR wirklich beenden?'):
            QApplication.quit()


# ==================== SEITE 2: MATCH-SETUP (MIT AUTOCOMPLETE) ====================
class MatchSetupPage(QWidget):
    """Seite zur manuellen Eingabe der Spielernamen mit Autocomplete."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.turniere = []
        self.keyboard = None  # Touch-Tastatur
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 30, 50, 30)
        
        # Titel
        title = QLabel("Match Setup")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # ===== Match-Typ Auswahl =====
        type_layout = QHBoxLayout()
        type_layout.setSpacing(30)
        
        lbl_type = QLabel("Match-Typ:")
        lbl_type.setStyleSheet("font-size: 20px; color: #888888;")
        type_layout.addWidget(lbl_type)
        
        self.radio_einzelmatch = QRadioButton("Einzelmatch")
        radio_style = """
            QRadioButton { font-size: 20px; color: #ffffff; spacing: 10px; }
            QRadioButton::indicator { width: 24px; height: 24px; }
            QRadioButton::indicator:checked { background-color: #00d9ff; border: 2px solid #00d9ff; border-radius: 12px; }
            QRadioButton::indicator:unchecked { background-color: #16213e; border: 2px solid #0f3460; border-radius: 12px; }
        """
        self.radio_einzelmatch.setStyleSheet(radio_style)
        self.radio_einzelmatch.setChecked(True)
        self.radio_einzelmatch.toggled.connect(self.on_type_changed)
        type_layout.addWidget(self.radio_einzelmatch)
        
        self.radio_turnier = QRadioButton("Turnier")
        self.radio_turnier.setStyleSheet(radio_style)
        type_layout.addWidget(self.radio_turnier)
        
        type_layout.addStretch()
        layout.addLayout(type_layout)
        
        # ===== Turnier-Auswahl (versteckt) =====
        self.turnier_container = QWidget()
        turnier_layout = QHBoxLayout(self.turnier_container)
        turnier_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_turnier = QLabel("Turnier:")
        lbl_turnier.setStyleSheet("font-size: 20px; color: #00d9ff;")
        turnier_layout.addWidget(lbl_turnier)
        
        self.combo_turnier = QComboBox()
        self.combo_turnier.setMinimumHeight(50)
        self.combo_turnier.setStyleSheet("""
            QComboBox { background-color: #16213e; color: #ffffff; border: 2px solid #0f3460; border-radius: 10px; padding: 10px; font-size: 18px; }
            QComboBox QAbstractItemView { background-color: #16213e; color: #ffffff; selection-background-color: #00d9ff; selection-color: #1a1a2e; }
        """)
        turnier_layout.addWidget(self.combo_turnier, 1)
        
        btn_new_turnier = QPushButton("+ Neu")
        btn_new_turnier.setMinimumHeight(50)
        btn_new_turnier.clicked.connect(self.on_new_turnier)
        turnier_layout.addWidget(btn_new_turnier)
        
        self.turnier_container.setVisible(False)
        layout.addWidget(self.turnier_container)
        
        # Separator
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(separator)
        
        # ===== Spieler Eingabe (mit Autocomplete) =====
        lbl_player1 = QLabel("Spieler 1 (Links)")
        lbl_player1.setStyleSheet("font-size: 22px; color: #00d9ff;")
        layout.addWidget(lbl_player1)
        
        self.input_player1 = QLineEdit()
        self.input_player1.setPlaceholderText("Name eingeben oder suchen...")
        self.input_player1.setMinimumHeight(55)
        layout.addWidget(self.input_player1)
        
        vs_label = QLabel("VS")
        vs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vs_label.setStyleSheet("font-size: 32px; color: #e94560;")
        layout.addWidget(vs_label)
        
        lbl_player2 = QLabel("Spieler 2 (Rechts)")
        lbl_player2.setStyleSheet("font-size: 22px; color: #00d9ff;")
        layout.addWidget(lbl_player2)
        
        self.input_player2 = QLineEdit()
        self.input_player2.setPlaceholderText("Name eingeben oder suchen...")
        self.input_player2.setMinimumHeight(55)
        layout.addWidget(self.input_player2)
        
        layout.addSpacing(20)
        
        # ===== Buttons =====
        btn_layout = QHBoxLayout()
        btn_back = QPushButton("← Zurück")
        btn_back.setMinimumHeight(70)
        btn_back.clicked.connect(self.on_back)
        btn_layout.addWidget(btn_back)
        
        btn_start = QPushButton("Match Starten")
        btn_start.setObjectName("primary")
        btn_start.setMinimumHeight(70)
        btn_start.clicked.connect(self.on_start)
        btn_layout.addWidget(btn_start)
        
        layout.addLayout(btn_layout)
        
        self.input_player1.setReadOnly(True)
        self.input_player2.setReadOnly(True)
        self.input_player1.mousePressEvent = lambda e: self.open_keyboard(self.input_player1, "Spieler 1")
        self.input_player2.mousePressEvent = lambda e: self.open_keyboard(self.input_player2, "Spieler 2")
        
        self.setLayout(layout)
    
    def open_keyboard(self, target_field, title="Eingabe"):
        """Öffnet die Vollbild-Tastatur für ein Eingabefeld."""
        if self.main_window:
            self.main_window.show_keyboard_for_field(target_field, 1, title)

    def showEvent(self, event):
        """Wird aufgerufen, sobald die Seite angezeigt wird -> Lädt Vorschläge neu."""
        self.refresh_autocomplete()
        super().showEvent(event)

    def refresh_autocomplete(self):
        """Lädt Spieler aus der DB und fügt sie zur Autovervollständigung hinzu."""
        if self.main_window and self.main_window.db:
            # Spielerliste laden (id, vorname, nachname)
            raw_players = self.main_window.db.get_spieler()
            
            # Nur Namen extrahieren: "Vorname Nachname"
            player_names = [f"{p[1]} {p[2]}" for p in raw_players]
            
            # Completer erstellen
            completer = QCompleter(player_names)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            
            # An die Textfelder binden
            self.input_player1.setCompleter(completer)
            self.input_player2.setCompleter(completer)

    def on_type_changed(self):
        is_turnier = self.radio_turnier.isChecked()
        self.turnier_container.setVisible(is_turnier)
        if is_turnier:
            self.load_turniere()
    
    def load_turniere(self):
        self.combo_turnier.clear()
        if self.main_window and self.main_window.db:
            self.turniere = self.main_window.db.get_turniere()
            for turnier in self.turniere:
                turnier_id, name, _ = turnier
                self.combo_turnier.addItem(name, turnier_id)
    
    def on_new_turnier(self):
        name, ok = TouchInputDialog.get_text(self, "Neues Turnier", "Turniername:")
        if ok and name.strip():
            if self.main_window and self.main_window.db:
                new_id = self.main_window.db.create_turnier(name.strip())
                self.load_turniere()
                for i in range(self.combo_turnier.count()):
                    if self.combo_turnier.itemData(i) == new_id:
                        self.combo_turnier.setCurrentIndex(i)
                        break
    
    def clear_inputs(self):
        self.input_player1.clear()
        self.input_player2.clear()
        self.radio_einzelmatch.setChecked(True)
        self.turnier_container.setVisible(False)
    
    def on_back(self):
        if self.main_window:
            self.main_window.show_start_menu()
    
    def on_start(self):
        player1_name = self.input_player1.text().strip()
        player2_name = self.input_player2.text().strip()
        
        if not player1_name or not player2_name:
            QMessageBox.warning(self, "Fehler", "Bitte gib beide Spielernamen ein!")
            return
        
        if player1_name.lower() == player2_name.lower():
            QMessageBox.warning(self, "Fehler", "Die Spielernamen müssen unterschiedlich sein!")
            return
        
        turnier_id = None
        turnier_name = None
        if self.radio_turnier.isChecked():
            if self.combo_turnier.count() == 0:
                QMessageBox.warning(self, "Fehler", "Bitte wähle ein Turnier aus!")
                return
            turnier_id = self.combo_turnier.currentData()
            turnier_name = self.combo_turnier.currentText()
        
        if self.main_window:
            self.main_window.current_turnier_id = turnier_id
            self.main_window.current_turnier_name = turnier_name
            self.main_window.page_scoreboard.turnier_id = turnier_id
            self.main_window.page_scoreboard.reset_match(None, player1_name, None, player2_name)
            self.main_window.stack.setCurrentIndex(4)


# ==================== SEITE 3: TURNIER-LISTE ====================
class TurnierListPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)
        
        title = QLabel("Turniere")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        self.turnier_list = QListWidget()
        self.turnier_list.setStyleSheet("""
            QListWidget { background-color: #16213e; border: 2px solid #0f3460; border-radius: 10px; padding: 10px; font-size: 20px; }
            QListWidget::item { padding: 15px; border-bottom: 1px solid #0f3460; color: #ffffff; }
            QListWidget::item:selected { background-color: #00d9ff; color: #1a1a2e; }
        """)
        self.turnier_list.itemDoubleClicked.connect(self.on_turnier_selected)
        layout.addWidget(self.turnier_list)
        
        btn_layout = QHBoxLayout()
        btn_back = QPushButton("← Zurück")
        btn_back.setMinimumHeight(70)
        btn_back.clicked.connect(self.on_back)
        btn_layout.addWidget(btn_back)
        
        btn_new = QPushButton("Neues Turnier")
        btn_new.setObjectName("primary")
        btn_new.setMinimumHeight(70)
        btn_new.clicked.connect(self.on_new_turnier)
        btn_layout.addWidget(btn_new)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def load_turniere(self):
        self.turnier_list.clear()
        if self.main_window and self.main_window.db:
            turniere = self.main_window.db.get_turniere()
            for turnier in turniere:
                turnier_id, name, _ = turnier
                item = QListWidgetItem(f"{name}")
                item.setData(Qt.ItemDataRole.UserRole, turnier_id)
                self.turnier_list.addItem(item)
    
    def on_back(self):
        if self.main_window:
            self.main_window.show_start_menu()
    
    def on_new_turnier(self):
        name, ok = QInputDialog.getText(self, "Neues Turnier", "Turniername:")
        if ok and name.strip():
            if self.main_window and self.main_window.db:
                self.main_window.db.create_turnier(name.strip())
                self.load_turniere()
    
    def on_turnier_selected(self, item):
        turnier_id = item.data(Qt.ItemDataRole.UserRole)
        turnier_name = item.text()
        if self.main_window:
            self.main_window.show_turnier_detail(turnier_id, turnier_name)


# ==================== SEITE 4: TURNIER-DETAIL ====================
class TurnierDetailPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.turnier_id = None
        self.turnier_name = ""
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        self.title_label = QLabel("Turnier")
        self.title_label.setObjectName("title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        content_layout = QHBoxLayout()
        
        # Matches Tabelle
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_title = QLabel("Match-Historie")
        left_title.setStyleSheet("font-size: 20px; color: #00d9ff; font-weight: bold;")
        left_layout.addWidget(left_title)
        
        self.match_table = QTableWidget()
        self.match_table.setColumnCount(4)
        self.match_table.setHorizontalHeaderLabels(["Spieler 1", "Spieler 2", "Ergebnis", "Datum"])
        self.match_table.horizontalHeader().setStretchLastSection(True)
        self.match_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.match_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.match_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.match_table.setStyleSheet("""
            QTableWidget { background-color: #16213e; border: 2px solid #0f3460; border-radius: 10px; font-size: 16px; }
            QHeaderView::section { background-color: #0f3460; color: #00d9ff; border: none; font-weight: bold; }
            QTableWidget::item { padding: 8px; color: #ffffff; }
        """)
        left_layout.addWidget(self.match_table)
        content_layout.addWidget(left_widget)
        
        # Rangliste
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_title = QLabel("Rangliste")
        right_title.setStyleSheet("font-size: 20px; color: #00d9ff; font-weight: bold;")
        right_layout.addWidget(right_title)
        
        self.rank_table = QTableWidget()
        self.rank_table.setColumnCount(3)
        self.rank_table.setHorizontalHeaderLabels(["Spieler", "Siege", "Niederlagen"])
        self.rank_table.horizontalHeader().setStretchLastSection(True)
        self.rank_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.rank_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.rank_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.rank_table.setStyleSheet("""
            QTableWidget { background-color: #16213e; border: 2px solid #0f3460; border-radius: 10px; font-size: 16px; }
            QHeaderView::section { background-color: #0f3460; color: #00d9ff; border: none; font-weight: bold; }
            QTableWidget::item { padding: 8px; color: #ffffff; }
        """)
        right_layout.addWidget(self.rank_table)
        content_layout.addWidget(right_widget)
        
        layout.addLayout(content_layout)
        
        btn_layout = QHBoxLayout()
        btn_back = QPushButton("← Zurück")
        btn_back.setMinimumHeight(60)
        btn_back.clicked.connect(self.on_back)
        btn_layout.addWidget(btn_back)
        
        btn_play = QPushButton("Match spielen")
        btn_play.setObjectName("primary")
        btn_play.setMinimumHeight(60)
        btn_play.clicked.connect(self.on_play_match)
        btn_layout.addWidget(btn_play)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def load_turnier(self, turnier_id, turnier_name):
        self.turnier_id = turnier_id
        self.turnier_name = turnier_name
        self.title_label.setText(turnier_name)
        
        if self.main_window and self.main_window.db:
            matches = self.main_window.db.get_turnier_matches(turnier_id)
            self.match_table.setRowCount(len(matches))
            for row, match in enumerate(matches):
                match_id, spieler1, spieler2, score1, score2, datum = match
                self.match_table.setItem(row, 0, QTableWidgetItem(spieler1))
                self.match_table.setItem(row, 1, QTableWidgetItem(spieler2))
                self.match_table.setItem(row, 2, QTableWidgetItem(f"{score1}:{score2}"))
                datum_str = str(datum)[:16] if datum else "-"
                self.match_table.setItem(row, 3, QTableWidgetItem(datum_str))
            
            rangliste = self.main_window.db.get_rangliste(turnier_id)
            self.rank_table.setRowCount(len(rangliste))
            for row, eintrag in enumerate(rangliste):
                name, siege, niederlagen = eintrag
                self.rank_table.setItem(row, 0, QTableWidgetItem(name))
                self.rank_table.setItem(row, 1, QTableWidgetItem(str(siege)))
                self.rank_table.setItem(row, 2, QTableWidgetItem(str(niederlagen)))
    
    def on_back(self):
        if self.main_window:
            self.main_window.show_turnier_list()
    
    def on_play_match(self):
        if self.main_window:
            self.main_window.start_turnier_match(self.turnier_id, self.turnier_name)


# ==================== SEITE 5: SCOREBOARD ====================
class ScoreboardPage(QWidget):
    """Das Hauptspiel-Scoreboard."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        
        self.player1_id = None
        self.player1_name = ""
        self.player2_id = None
        self.player2_name = ""
        self.score1 = 0
        self.score2 = 0
        self.sets1 = 0
        self.sets2 = 0
        self.sets_to_win = 3
        self.turnier_id = None
        
        # Aufschlag-Tracking: 1 = Spieler 1, 2 = Spieler 2
        self.server = 1
        self.initial_server = 1
        
        # Konfetti-Overlays
        self.confetti_overlay1 = None
        self.confetti_overlay2 = None
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ===== Haupt-Layout =====
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        
        # Spieler 1 Bereich (Satz + Name oben, Punkt unten)
        self.player1_container = QWidget()
        player1_area = QVBoxLayout(self.player1_container)
        player1_area.setSpacing(0)
        player1_area.setContentsMargins(0, 0, 0, 0)
        
        # Obere Zeile: Satz + Name (mit Serve-Indicator)
        name1_row = QHBoxLayout()
        
        # Satz-Anzeige Spieler 1
        self.lbl_sets1 = QLabel("0")
        self.lbl_sets1.setObjectName("setScore")
        self.lbl_sets1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_sets1.setFixedWidth(150)
        name1_row.addWidget(self.lbl_sets1)
        
        name1_row.addStretch()
        self.lbl_player1_name = QLabel("Spieler 1")
        self.lbl_player1_name.setObjectName("playerName")
        self.lbl_player1_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name1_row.addWidget(self.lbl_player1_name)
        self.serve_indicator1 = QLabel("●")
        self.serve_indicator1.setStyleSheet("font-size: 32px; color: white; margin-left: 10px;")
        name1_row.addWidget(self.serve_indicator1)
        name1_row.addStretch()
        player1_area.addLayout(name1_row)
        
        # Punkt (klickbar, zentriert)
        self.lbl_score1 = QLabel("0")
        self.lbl_score1.setObjectName("scoreBig")
        self.lbl_score1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_score1.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_score1.mousePressEvent = lambda e: self.add_point(1)
        player1_area.addWidget(self.lbl_score1, 1)
        
        # Konfetti-Overlay für Spieler 1
        self.confetti_overlay1 = ConfettiOverlay(self.player1_container, "left")
        
        main_layout.addWidget(self.player1_container, 1)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet("background-color: #0f3460; max-width: 3px;")
        main_layout.addWidget(separator)
        
        # Spieler 2 Bereich (Name + Satz oben, Punkt unten)
        self.player2_container = QWidget()
        player2_area = QVBoxLayout(self.player2_container)
        player2_area.setSpacing(0)
        player2_area.setContentsMargins(0, 0, 0, 0)
        
        # Obere Zeile: Name (mit Serve-Indicator) + Satz
        name2_row = QHBoxLayout()
        name2_row.addStretch()
        self.serve_indicator2 = QLabel("●")
        self.serve_indicator2.setStyleSheet("font-size: 32px; color: transparent; margin-right: 10px;")
        name2_row.addWidget(self.serve_indicator2)
        self.lbl_player2_name = QLabel("Spieler 2")
        self.lbl_player2_name.setObjectName("playerName")
        self.lbl_player2_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name2_row.addWidget(self.lbl_player2_name)
        name2_row.addStretch()
        
        # Satz-Anzeige Spieler 2
        self.lbl_sets2 = QLabel("0")
        self.lbl_sets2.setObjectName("setScore")
        self.lbl_sets2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_sets2.setFixedWidth(150)
        name2_row.addWidget(self.lbl_sets2)
        
        player2_area.addLayout(name2_row)
        
        # Punkt (klickbar, zentriert)
        self.lbl_score2 = QLabel("0")
        self.lbl_score2.setObjectName("scoreBig")
        self.lbl_score2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_score2.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_score2.mousePressEvent = lambda e: self.add_point(2)
        player2_area.addWidget(self.lbl_score2, 1)
        
        # Konfetti-Overlay für Spieler 2
        self.confetti_overlay2 = ConfettiOverlay(self.player2_container, "right")
        
        main_layout.addWidget(self.player2_container, 1)
        
        layout.addLayout(main_layout, 1)
        
        # ===== Handle Button - schmaler Balken mit Pfeil innen =====
        handle_wrapper = QWidget()
        handle_wrapper_layout = QHBoxLayout(handle_wrapper)
        handle_wrapper_layout.setContentsMargins(0, 5, 0, 0)
        handle_wrapper_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Balken mit Pfeil innen
        self.dropdown_handle = QPushButton("▲")
        self.dropdown_handle.setFixedSize(268, 24)  # Höher für zentrierten Pfeil
        self.dropdown_handle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dropdown_expanded = False
        self.update_dropdown_handle()
        self.dropdown_handle.clicked.connect(self.toggle_dropdown)
        handle_wrapper_layout.addWidget(self.dropdown_handle)
        layout.addWidget(handle_wrapper)
        
        # ===== Button Container (versteckt, volle Breite wie im Bild) =====
        self.dropdown_buttons = QWidget()
        self.dropdown_buttons.setVisible(False)
        self.dropdown_buttons.setStyleSheet("background-color: #1a1a2e;")
        btn_layout = QHBoxLayout(self.dropdown_buttons)
        btn_layout.setSpacing(15)
        btn_layout.setContentsMargins(30, 15, 30, 20)
        
        btn_quit = QPushButton("Abbrechen")
        btn_quit.setObjectName("danger")
        btn_quit.setMinimumHeight(55)
        btn_quit.clicked.connect(self.on_quit)
        btn_layout.addWidget(btn_quit)
        
        btn_undo = QPushButton("Rückgängig")
        btn_undo.setMinimumHeight(55)
        btn_undo.setStyleSheet("""
            QPushButton {
                background-color: #16213e;
                color: #ffffff;
                border: 2px solid #00d9ff;
                border-radius: 15px;
                padding: 15px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00d9ff;
                color: #1a1a2e;
            }
        """)
        btn_undo.clicked.connect(self.on_undo)
        btn_layout.addWidget(btn_undo)
        
        layout.addWidget(self.dropdown_buttons)
        
        self.setLayout(layout)
    
    def update_dropdown_handle(self):
        """Aktualisiert den Handle-Style basierend auf Zustand."""
        # Farbdesign wie Rückgängig-Button mit runderen Ecken
        if self.dropdown_expanded:
            # Aktiver Zustand - heller, Pfeil nach unten
            self.dropdown_handle.setText("▼")
            self.dropdown_handle.setStyleSheet("""
                QPushButton {
                    background-color: #00d9ff;
                    color: #1a1a2e;
                    border: none;
                    border-radius: 6px;
                    font-size: 16px;
                    padding-top: -8px;
                }
            """)
        else:
            # Normaler Zustand
            self.dropdown_handle.setText("▲")
            self.dropdown_handle.setStyleSheet("""
                QPushButton {
                    background-color: #16213e;
                    color: #888888;
                    border: 2px solid #444444;
                    border-radius: 6px;
                    font-size: 16px;
                    padding-top: -8px;
                }
            """)
    
    def toggle_dropdown(self):
        """Öffnet/Schliesst das Dropdown-Menu."""
        self.dropdown_expanded = not self.dropdown_expanded
        self.dropdown_buttons.setVisible(self.dropdown_expanded)
        self.update_dropdown_handle()
    
    def reset_match(self, player1_id, player1_name, player2_id, player2_name):
        self.player1_id = player1_id
        self.player1_name = player1_name
        self.player2_id = player2_id
        self.player2_name = player2_name
        
        self.score1 = 0
        self.score2 = 0
        self.sets1 = 0
        self.sets2 = 0
        self.history = []
        
        # Aufschlag-Auswahl anzeigen
        self.choose_initial_server()
        self.update_display()
    
    def choose_initial_server(self):
        """Zeigt Dialog zur Auswahl des ersten Aufschlägers."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Aufschlag")
        msg_box.setText("Wer hat Aufschlag?")
        msg_box.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        msg_box.setStyleSheet("""
            QMessageBox { background-color: #1a1a2e; border: 3px solid #00d9ff; border-radius: 15px; }
            QLabel { color: white; font-size: 26px; margin: 20px; font-weight: bold; }
            QPushButton { background-color: #16213e; color: white; border: 2px solid #0f3460; border-radius: 10px; padding: 15px 30px; font-size: 20px; min-width: 120px; min-height: 50px; }
            QPushButton:hover { background-color: #00d9ff; color: #1a1a2e; }
        """)
        
        btn_player1 = msg_box.addButton(self.player1_name, QMessageBox.ButtonRole.YesRole)
        btn_player2 = msg_box.addButton(self.player2_name, QMessageBox.ButtonRole.NoRole)
        
        msg_box.exec()
        
        if msg_box.clickedButton() == btn_player1:
            self.server = 1
        else:
            self.server = 2
        
        self.initial_server = self.server
    
    def update_display(self):
        self.lbl_player1_name.setText(self.player1_name)
        self.lbl_player2_name.setText(self.player2_name)
        self.lbl_score1.setText(str(self.score1))
        self.lbl_score2.setText(str(self.score2))
        self.lbl_sets1.setText(str(self.sets1))
        self.lbl_sets2.setText(str(self.sets2))
        self.update_serve_indicator()
    
    def update_serve_indicator(self):
        """Zeigt/versteckt den Aufschlag-Punkt."""
        if self.server == 1:
            self.serve_indicator1.setStyleSheet("font-size: 32px; color: white; margin-left: 10px;")
            self.serve_indicator2.setStyleSheet("font-size: 32px; color: transparent; margin-right: 10px;")
        else:
            self.serve_indicator1.setStyleSheet("font-size: 32px; color: transparent; margin-left: 10px;")
            self.serve_indicator2.setStyleSheet("font-size: 32px; color: white; margin-right: 10px;")
    
    def check_serve_change(self):
        """Prüft ob Aufschlag wechseln muss (alle 2 Punkte, in Verlängerung jeder Punkt)."""
        total_points = self.score1 + self.score2
        
        # Bei Verlängerung (beide >= 10): Wechsel nach jedem Punkt
        if self.score1 >= 10 and self.score2 >= 10:
            self.server = 1 if self.server == 2 else 2
        else:
            # Normal: Wechsel alle 2 Punkte
            if total_points % 2 == 0 and total_points > 0:
                self.server = 1 if self.server == 2 else 2
    
    def add_point(self, player):
        self.history.append((self.score1, self.score2, self.sets1, self.sets2, self.server))
        
        if player == 1:
            self.score1 += 1
        else:
            self.score2 += 1
        
        self.check_serve_change()
        self.update_display()
        self.check_set_win()
    
    def check_set_win(self):
        if self.score1 >= 11 and self.score1 - self.score2 >= 2:
            self.sets1 += 1
            self.show_set_won(1)
        elif self.score2 >= 11 and self.score2 - self.score1 >= 2:
            self.sets2 += 1
            self.show_set_won(2)
    
    def show_set_won(self, player):
        self.update_display()
        if self.sets1 >= self.sets_to_win:
            self.match_won(1)
        elif self.sets2 >= self.sets_to_win:
            self.match_won(2)
        else:
            winner_name = self.player1_name if player == 1 else self.player2_name
            
            # Konfetti auf der Gewinnerseite starten
            if player == 1 and self.confetti_overlay1:
                self.confetti_overlay1.setGeometry(0, 0, self.player1_container.width(), self.player1_container.height())
                self.confetti_overlay1.start_confetti()
            elif player == 2 and self.confetti_overlay2:
                self.confetti_overlay2.setGeometry(0, 0, self.player2_container.width(), self.player2_container.height())
                self.confetti_overlay2.start_confetti()
            
            # Rahmenloses Popup für den Satzgewinn (stoppt Konfetti automatisch durch Klick)
            confirmed = show_custom_info_dialog(self, "Satz gewonnen!", f"{winner_name} gewinnt den Satz!\nStand: {self.sets1} : {self.sets2}", cancel_text="Zurück")
            
            # Konfetti stoppen falls noch aktiv
            if self.confetti_overlay1:
                self.confetti_overlay1.stop_confetti()
            if self.confetti_overlay2:
                self.confetti_overlay2.stop_confetti()
            
            if confirmed:
                self.score1 = 0
                self.score2 = 0
                # Aufschlag wechselt nach jedem Satz
                self.initial_server = 1 if self.initial_server == 2 else 2
                self.server = self.initial_server
                self.update_display()
            else:
                # ABBRECHEN: Exakt den letzten Punkt (der zum Satzgewinn führte) rückgängig machen
                self.on_undo()
    
    def match_won(self, player):
        winner_name = self.player1_name if player == 1 else self.player2_name
        
        # Konfetti auf der Gewinnerseite starten
        if player == 1 and self.confetti_overlay1:
            self.confetti_overlay1.setGeometry(0, 0, self.player1_container.width(), self.player1_container.height())
            self.confetti_overlay1.start_confetti()
        elif player == 2 and self.confetti_overlay2:
            self.confetti_overlay2.setGeometry(0, 0, self.player2_container.width(), self.player2_container.height())
            self.confetti_overlay2.start_confetti()
        
        # Rahmenloses Popup
        confirmed = show_custom_info_dialog(self, "MATCH GEWONNEN!", f"{winner_name} gewinnt das Match!\nEndstand: {self.sets1} : {self.sets2}", cancel_text="Zurück")
        
        # Konfetti stoppen
        if self.confetti_overlay1:
            self.confetti_overlay1.stop_confetti()
        if self.confetti_overlay2:
            self.confetti_overlay2.stop_confetti()
        
        if confirmed:
            # ERST JETZT in DB speichern
            if self.main_window and self.main_window.db:
                self.main_window.db.save_match_with_names(self.player1_name, self.player2_name, self.sets1, self.sets2, self.turnier_id)
            
            if self.main_window:
                if self.turnier_id and self.main_window.current_turnier_name:
                    self.main_window.show_turnier_detail(self.turnier_id, self.main_window.current_turnier_name)
                else:
                    self.main_window.show_start_menu()
        else:
            # ABBRECHEN: Exakt den letzten Punkt (der zum Matchgewinn führte) rückgängig machen
            self.on_undo()
    
    def on_undo(self):
        if self.history:
            self.score1, self.score2, self.sets1, self.sets2, self.server = self.history.pop()
            self.update_display()
    
    def on_quit(self):
        # HIER: Neues, rahmenloses Popup beim Abbrechen
        if show_custom_confirm_dialog(self, 'Abbrechen', 'Match abbrechen ohne Speichern?'):
            if self.main_window:
                if self.turnier_id and self.main_window.current_turnier_name:
                    self.main_window.show_turnier_detail(self.turnier_id, self.main_window.current_turnier_name)
                else:
                    self.main_window.show_start_menu()


# ==================== HAUPTFENSTER ====================
class TTRMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.db.connect()
        
        self.current_turnier_id = None
        self.current_turnier_name = None
        
        self.setup_ui()
        self.setWindowTitle("TTR - Table Tennis Referee")
        self.setMinimumSize(800, 600)
    
    def setup_ui(self):
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        self.page_start = StartMenuPage(self)
        self.page_setup = MatchSetupPage(self)
        self.page_turnier_list = TurnierListPage(self)
        self.page_turnier_detail = TurnierDetailPage(self)
        self.page_scoreboard = ScoreboardPage(self)
        self.page_keyboard = FullscreenKeyboardPage(self)  # Vollbild-Tastatur
        
        self.stack.addWidget(self.page_start)          # 0
        self.stack.addWidget(self.page_setup)          # 1
        self.stack.addWidget(self.page_turnier_list)   # 2
        self.stack.addWidget(self.page_turnier_detail) # 3
        self.stack.addWidget(self.page_scoreboard)     # 4
        self.stack.addWidget(self.page_keyboard)       # 5
        
        self.stack.setCurrentIndex(0)
    
    def show_keyboard_for_field(self, target_field, return_index, title="Eingabe"):
        """Öffnet Vollbild-Tastatur für ein Eingabefeld."""
        def on_keyboard_close():
            self.stack.setCurrentIndex(return_index)
        
        self.page_keyboard.open_for_field(target_field, on_keyboard_close, title)
        self.stack.setCurrentIndex(5)
    
    def show_start_menu(self):
        self.current_turnier_id = None
        self.current_turnier_name = None
        self.stack.setCurrentIndex(0)
    
    def show_match_setup(self):
        self.current_turnier_id = None
        self.current_turnier_name = None
        self.page_setup.clear_inputs()
        self.stack.setCurrentIndex(1)
    
    def show_turnier_list(self):
        self.page_turnier_list.load_turniere()
        self.stack.setCurrentIndex(2)
    
    def show_turnier_detail(self, turnier_id, turnier_name):
        self.page_turnier_detail.load_turnier(turnier_id, turnier_name)
        self.stack.setCurrentIndex(3)
    
    def start_match(self, player1_id, player1_name, player2_id, player2_name):
        self.page_scoreboard.reset_match(player1_id, player1_name, player2_id, player2_name)
        self.page_scoreboard.turnier_id = None
        self.stack.setCurrentIndex(4)
    
    def start_turnier_match(self, turnier_id, turnier_name):
        self.current_turnier_id = turnier_id
        self.current_turnier_name = turnier_name
        self.page_setup.clear_inputs()
        self.stack.setCurrentIndex(1)
    
    def closeEvent(self, event):
        self.db.disconnect()
        event.accept()


# ==================== HAUPTPROGRAMM ====================
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLESHEET)
    
    font = QFont()
    font.setPointSize(14)
    app.setFont(font)
    
    window = TTRMainWindow()
    
    # HIER: Vollbild-Modus aktivieren (Kiosk Mode)
    window.showFullScreen()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()