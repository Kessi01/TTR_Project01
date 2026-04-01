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
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QStackedWidget, QLineEdit, QFrame,
    QSizePolicy, QSpacerItem, QListWidget, QListWidgetItem, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView,
    QComboBox, QRadioButton, QButtonGroup, QCompleter, QDialog
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush, QKeyEvent
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

    def key_press(event: QKeyEvent):
        if event.key() == Qt.Key.Key_Right:
            dialog.accept()
        elif event.key() == Qt.Key.Key_Left:
            dialog.reject()
        else:
            QDialog.keyPressEvent(dialog, event)
    dialog.keyPressEvent = key_press

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

    # Nein Button (Rot, links)
    btn_no = QPushButton("Nein")
    btn_no.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    btn_no.setAutoDefault(False)
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

    # Ja Button (Blau, rechts)
    btn_yes = QPushButton("Ja")
    btn_yes.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    btn_yes.setAutoDefault(False)
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

    def key_press(event: QKeyEvent):
        if event.key() == Qt.Key.Key_Right:
            dialog.accept()
        elif event.key() == Qt.Key.Key_Left:
            dialog.reject()
        else:
            QDialog.keyPressEvent(dialog, event)
    dialog.keyPressEvent = key_press

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
    
    # Optionaler Cancel Button (links, rot)
    if cancel_text:
        btn_cancel = QPushButton(cancel_text)
        btn_cancel.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_cancel.setAutoDefault(False)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
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

    # OK Button (rechts, blau)
    btn_ok = QPushButton("OK")
    btn_ok.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    btn_ok.setAutoDefault(False)
    btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
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
    
    def open_for_field(self, target_line_edit, callback, title="Eingabe", show_suggestions=True):
        """Öffnet Tastatur für ein bestimmtes Feld.

        Args:
            show_suggestions: False um Dropdown-Button und Vorschlagsliste zu verstecken.
        """
        self.target_field = target_line_edit
        self.callback = callback
        self.input_field.setText(target_line_edit.text())
        self.shift_active = False
        self.suggestions_list.hide()
        self.title_label.setText(title)
        self.btn_dropdown.setVisible(show_suggestions)
        if show_suggestions:
            self.load_suggestions()
        else:
            self.all_suggestions = []
    
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

class TouchKeyboard(QWidget):
    """Wiederverwendbare Touch-Tastatur Komponente."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.target_field = None
        self.shift_active = False
        self.letter_buttons = []  # Referenzen für Buchstaben-Tasten
        self.shift_btn = None
        self.setup_ui()
        
    def set_target(self, target_line_edit):
        self.target_field = target_line_edit
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Schweizer QWERTZ Layout
        rows = [
            ['Q', 'W', 'E', 'R', 'T', 'Z', 'U', 'I', 'O', 'P', 'Ü'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Ö', 'Ä'],
            ['⇧', 'Y', 'X', 'C', 'V', 'B', 'N', 'M', '⌫'],
            [' ', '___SPACE___', ' '] # Vereinfacht
        ]
        
        for row in rows:
            row_layout = QHBoxLayout()
            row_layout.setSpacing(6)
            
            for key in row:
                if key == ' ': # Spacer
                    continue
                    
                btn = QPushButton()
                btn.setMinimumHeight(60)
                
                actual_key = key
                
                if key == '___SPACE___':
                    btn.setText("SPACE")
                    btn.setMinimumWidth(300)
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #3a3a4a;
                            color: white;
                            border: none;
                            border-radius: 8px;
                            font-size: 18px;
                        }
                        QPushButton:pressed { background-color: #5a5a6a; }
                    """)
                    actual_key = ' '
                elif key == '⌫':
                    btn.setText("⌫")
                    btn.setMinimumWidth(60)
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
                    actual_key = key
                elif key == '⇧':
                    btn.setText("⇧")
                    btn.setMinimumWidth(50)
                    self.shift_btn = btn
                    self.update_shift_button_style()
                    actual_key = key
                else:
                    btn.setText(key.lower())
                    btn.setMinimumWidth(45)
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #4a4a5a;
                            color: white;
                            border: none;
                            border-radius: 8px;
                            font-size: 20px;
                            font-weight: bold;
                        }
                        QPushButton:pressed { background-color: #6a6a7a; }
                    """)
                    actual_key = key
                    self.letter_buttons.append((btn, key))
                
                btn.clicked.connect(lambda checked, k=actual_key: self.key_pressed(k))
                row_layout.addWidget(btn)
            
            layout.addLayout(row_layout)
            
    def update_shift_button_style(self):
        if self.shift_btn:
            if self.shift_active:
                self.shift_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #00d9ff;
                        color: #1a1a2e;
                        border: none;
                        border-radius: 8px;
                        font-size: 20px;
                    }
                """)
            else:
                self.shift_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3a3a4a;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-size: 20px;
                    }
                    QPushButton:pressed { background-color: #5a5a6a; }
                """)
        
        for btn, key in self.letter_buttons:
            if self.shift_active:
                btn.setText(key.upper())
            else:
                btn.setText(key.lower())

    def key_pressed(self, key):
        if not self.target_field:
            return
            
        current = self.target_field.text()
        
        if key == '⌫':
            self.target_field.setText(current[:-1])
        elif key == '⇧':
            self.shift_active = not self.shift_active
            self.update_shift_button_style()
        else:
            char = key.lower() if not self.shift_active else key.upper()
            self.target_field.setText(current + char)
            
            if self.shift_active:
                self.shift_active = False
                self.update_shift_button_style()
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


class NewTurnierDialog(QDialog):
    """Dialog zum Erstellen eines Turniers mit Regelauswahl."""
    
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.result_name = ""
        self.result_sets = 3
        self.accepted = False
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
                border: 3px solid #00d9ff;
                border-radius: 15px;
            }
            QLabel { color: white; font-size: 20px; }
        """)
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Titel
        title = QLabel("Neues Turnier")
        title.setStyleSheet("font-size: 28px; color: #00d9ff; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Name Input
        layout.addWidget(QLabel("Name:"))
        self.input_name = QLineEdit()
        self.input_name.setMinimumHeight(60)
        self.input_name.setStyleSheet("""
            QLineEdit {
                background-color: #16213e;
                color: white;
                border: 2px solid #0f3460;
                border-radius: 10px;
                padding: 10px;
                font-size: 24px;
            }
        """)
        layout.addWidget(self.input_name)
        
        # Keyboard Integration
        self.keyboard = TouchKeyboard(self)
        self.keyboard.set_target(self.input_name)
        layout.addWidget(self.keyboard)
        
        # Modus Auswahl
        layout.addWidget(QLabel("Regeln:"))
        self.combo_sets = QComboBox()
        self.combo_sets.setMinimumHeight(60)
        self.combo_sets.setStyleSheet("""
            QComboBox {
                background-color: #16213e;
                color: white;
                border: 2px solid #00d9ff;
                border-radius: 10px;
                padding: 10px;
                font-size: 20px;
            }
        """)
        self.combo_sets.addItems(["Best of 3 (2 Gewinnsätze)", "Best of 5 (3 Gewinnsätze)", "Best of 7 (4 Gewinnsätze)"])
        self.combo_sets.setCurrentIndex(1) # Default: Best of 5
        layout.addWidget(self.combo_sets)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        btn_cancel = QPushButton("Abbrechen")
        btn_cancel.setMinimumHeight(60)
        btn_cancel.setStyleSheet("""
            QPushButton { background-color: #16213e; color: white; border: 2px solid #e94560; border-radius: 10px; font-size: 20px; }
            QPushButton:hover { background-color: #e94560; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        btn_ok = QPushButton("Erstellen")
        btn_ok.setMinimumHeight(60)
        btn_ok.setStyleSheet("""
            QPushButton { background-color: #16213e; color: white; border: 2px solid #00d9ff; border-radius: 10px; font-size: 20px; font-weight: bold; }
            QPushButton:hover { background-color: #00d9ff; color: #1a1a2e; }
        """)
        btn_ok.clicked.connect(self.on_accept)
        btn_layout.addWidget(btn_ok)
        
        layout.addLayout(btn_layout)
        
    def on_accept(self):
        self.result_name = self.input_name.text()
        idx = self.combo_sets.currentIndex()
        # 0->2 sets, 1->3 sets, 2->4 sets
        self.result_sets = idx + 2
        self.accept()

    @staticmethod
    def get_turnier_info(parent):
        dialog = NewTurnierDialog(parent)
        if parent:
            # Zentrieren
            parent_rect = parent.window().geometry()
            dialog.move(
                parent_rect.center().x() - dialog.width() // 2,
                parent_rect.center().y() - dialog.height() // 2
            )

        result = dialog.exec() == QDialog.DialogCode.Accepted
        return dialog.result_name, dialog.result_sets, result


# ==================== NEUES TURNIER: VOLLBILD ====================
class NeuTurnierPage(QWidget):
    """Vollbild-Ansicht zum Erstellen eines neuen Turniers.

    Gleicher Look & Feel wie die Spielernamenseingabe mit der Fullscreen-Tastatur.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.return_index = 1
        self.on_created_callback = None
        self.selected_sets = 3  # Default: Best of 5 (3 Gewinnsätze)
        self._rules_buttons = []
        self.setup_ui()

    def setup_ui(self):
        # Scope the background only to THIS widget, not to child buttons
        self.setObjectName("NeuTurnierPage")
        self.setStyleSheet("#NeuTurnierPage { background-color: #1a1a2e; }")

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(50, 40, 50, 40)

        # ===== Titel =====
        title = QLabel("Neues Turnier")
        title.setStyleSheet("font-size: 32px; color: #00d9ff; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        layout.addStretch(1)

        # ===== Turniername =====
        lbl_name = QLabel("Turniername")
        lbl_name.setStyleSheet("font-size: 20px; color: #888888; margin-bottom: 6px;")
        layout.addWidget(lbl_name)

        layout.addSpacing(8)

        self.input_name = QLineEdit()
        self.input_name.setMinimumHeight(80)
        self.input_name.setReadOnly(True)
        self.input_name.setPlaceholderText("Tippen zum Eingeben...")
        self.input_name.setCursor(Qt.CursorShape.PointingHandCursor)
        self.input_name.setStyleSheet("""
            QLineEdit {
                background-color: #16213e;
                color: white;
                border: 3px solid #00d9ff;
                border-radius: 15px;
                padding: 15px;
                font-size: 32px;
            }
            QLineEdit:focus { border-color: #00d9ff; }
        """)
        self.input_name.mousePressEvent = lambda e: self._open_keyboard()
        layout.addWidget(self.input_name)

        layout.addStretch(1)

        # ===== Regeln =====
        lbl_rules = QLabel("Regeln")
        lbl_rules.setStyleSheet("font-size: 20px; color: #888888; margin-bottom: 6px;")
        layout.addWidget(lbl_rules)

        layout.addSpacing(8)

        rules_layout = QHBoxLayout()
        rules_layout.setSpacing(15)
        for sets_val, label, sub in [(2, "Best of 3", "2 Gewinnsätze"),
                                     (3, "Best of 5", "3 Gewinnsätze"),
                                     (4, "Best of 7", "4 Gewinnsätze")]:
            btn = QPushButton(f"{label}\n{sub}")
            btn.setMinimumHeight(80)
            btn.clicked.connect(lambda checked, v=sets_val: self._select_rules(v))
            rules_layout.addWidget(btn)
            self._rules_buttons.append((btn, sets_val))
        layout.addLayout(rules_layout)

        layout.addStretch(2)

        # ===== Buttons =====
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)

        btn_cancel = QPushButton("← Abbrechen")
        btn_cancel.setMinimumHeight(75)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #16213e;
                color: #ffffff;
                border: 2px solid #0f3460;
                border-radius: 15px;
                font-size: 20px;
            }
            QPushButton:pressed { background-color: #0f3460; }
        """)
        btn_cancel.clicked.connect(self._on_cancel)
        btn_layout.addWidget(btn_cancel)

        btn_create = QPushButton("Turnier Erstellen")
        btn_create.setMinimumHeight(75)
        btn_create.setStyleSheet("""
            QPushButton {
                background-color: #00d9ff;
                color: #1a1a2e;
                border: none;
                border-radius: 15px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:pressed { background-color: #00b8d4; }
        """)
        btn_create.clicked.connect(self._on_create)
        btn_layout.addWidget(btn_create)

        layout.addLayout(btn_layout)

        self._update_rules_styles()

    def _update_rules_styles(self):
        for btn, val in self._rules_buttons:
            if val == self.selected_sets:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #00d9ff;
                        color: #1a1a2e;
                        border: none;
                        border-radius: 15px;
                        font-size: 20px;
                        font-weight: bold;
                        padding: 10px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #16213e;
                        color: #ffffff;
                        border: 2px solid #0f3460;
                        border-radius: 15px;
                        font-size: 20px;
                        padding: 10px;
                    }
                    QPushButton:pressed { background-color: #0f3460; }
                """)

    def _select_rules(self, sets_val):
        self.selected_sets = sets_val
        self._update_rules_styles()

    def _open_keyboard(self):
        if self.main_window:
            self.main_window.show_keyboard_for_field(
                self.input_name, 6, "Turniername", show_suggestions=False
            )

    def open(self, return_index, on_created_callback=None):
        """Bereitet die Seite vor und setzt Return-Zustand."""
        self.return_index = return_index
        self.on_created_callback = on_created_callback
        self.input_name.clear()
        self.selected_sets = 3
        self._update_rules_styles()

    def _on_cancel(self):
        if self.main_window:
            self.main_window.stack.setCurrentIndex(self.return_index)

    def _on_create(self):
        name = self.input_name.text().strip()
        if not name:
            show_custom_info_dialog(self, "Fehler", "Bitte gib einen Turniernamen ein!")
            return
        tid = None
        if self.main_window and self.main_window.db:
            tid = self.main_window.db.create_turnier(name, self.selected_sets)
        if self.on_created_callback:
            self.on_created_callback(tid, name)
        if self.main_window:
            self.main_window.stack.setCurrentIndex(self.return_index)


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
                self.ensure_schema()
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

    def ensure_schema(self):
        """Prüft und aktualisiert das Datenbankschema."""
        try:
            cursor = self.connection.cursor()
            # Prüfen ob Spalte sets_to_win in turniere existiert
            cursor.execute("SHOW COLUMNS FROM turniere LIKE 'sets_to_win'")
            result = cursor.fetchone()
            if not result:
                print("⚠️ Spalte 'sets_to_win' fehlt in 'turniere'. Füge hinzu...")
                cursor.execute("ALTER TABLE turniere ADD COLUMN sets_to_win INT DEFAULT 3")
                self.connection.commit()
                print("✅ Schema aktualisiert.")
            # Tabelle match_sets erstellen falls nicht vorhanden
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS match_sets (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    match_id INT NOT NULL,
                    set_nummer INT NOT NULL,
                    punkte_s1 INT NOT NULL,
                    punkte_s2 INT NOT NULL,
                    FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE
                )
            """)
            self.connection.commit()
            cursor.close()
        except Error as e:
            print(f"❌ Fehler bei Schema-Prüfung: {e}")
    
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
        """Speichert ein Match-Ergebnis in der Datenbank. Gibt match_id zurück oder None bei Fehler."""
        if not MYSQL_AVAILABLE or not self.connection:
            print(f"💾 Match gespeichert (Dummy): {spieler1_id} vs {spieler2_id}")
            return None

        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO matches (spieler1_id, spieler2_id, satz_score_s1, satz_score_s2, turnier_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (spieler1_id, spieler2_id, satz_score_s1, satz_score_s2, turnier_id))
            self.connection.commit()
            match_id = cursor.lastrowid
            cursor.close()
            print(f"✅ Match gespeichert (ID: {match_id}).")
            return match_id
        except Error as e:
            print(f"❌ Fehler beim Speichern des Matches: {e}")
            return None

    def save_match_sets(self, match_id, set_scores):
        """Speichert die Einzel-Satz-Ergebnisse eines Matches.

        Args:
            match_id: ID des Matches
            set_scores: Liste von (punkte_s1, punkte_s2) Tupeln, in Satz-Reihenfolge
        """
        if not MYSQL_AVAILABLE or not self.connection or not match_id or not set_scores:
            return
        try:
            cursor = self.connection.cursor()
            for i, (p1, p2) in enumerate(set_scores, start=1):
                cursor.execute(
                    "INSERT INTO match_sets (match_id, set_nummer, punkte_s1, punkte_s2) VALUES (%s, %s, %s, %s)",
                    (match_id, i, p1, p2)
                )
            self.connection.commit()
            cursor.close()
            print(f"✅ {len(set_scores)} Sätze gespeichert.")
        except Error as e:
            print(f"❌ Fehler beim Speichern der Sätze: {e}")
    
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
    
    def save_match_with_names(self, spieler1_name, spieler2_name, satz_score_s1, satz_score_s2, turnier_id=None, set_scores=None):
        spieler1_id = self.get_or_create_spieler(spieler1_name)
        spieler2_id = self.get_or_create_spieler(spieler2_name)

        if spieler1_id is None or spieler2_id is None:
            return False

        match_id = self.save_match(spieler1_id, spieler2_id, satz_score_s1, satz_score_s2, turnier_id)
        if match_id and set_scores:
            self.save_match_sets(match_id, set_scores)
        return match_id is not None
    
    # ==================== TURNIER-METHODEN ====================
    def get_turniere(self):
        if not MYSQL_AVAILABLE or not self.connection:
            return []
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id, name, erstellt_am, sets_to_win FROM turniere ORDER BY erstellt_am DESC")
            turniere = cursor.fetchall()
            cursor.close()
            return turniere
        except Error as e:
            print(f"❌ Fehler beim Laden der Turniere: {e}")
            return []
    
    def create_turnier(self, name, sets_to_win=3):
        if not MYSQL_AVAILABLE or not self.connection:
            return 1
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO turniere (name, sets_to_win) VALUES (%s, %s)", (name, sets_to_win))
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
        """Rangliste mit Siegen, Niederlagen, Sätzen und Satzdifferenz."""
        if not MYSQL_AVAILABLE or not self.connection:
            return []
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT name, siege, niederlagen, saetze_gewonnen, saetze_verloren,
                       (saetze_gewonnen - saetze_verloren) as satzdiff
                FROM (
                    SELECT
                        CONCAT(s.vorname, ' ', s.nachname) as name,
                        SUM(CASE
                            WHEN (m.spieler1_id = s.id AND m.satz_score_s1 > m.satz_score_s2)
                              OR (m.spieler2_id = s.id AND m.satz_score_s2 > m.satz_score_s1)
                            THEN 1 ELSE 0 END) as siege,
                        SUM(CASE
                            WHEN (m.spieler1_id = s.id AND m.satz_score_s1 < m.satz_score_s2)
                              OR (m.spieler2_id = s.id AND m.satz_score_s2 < m.satz_score_s1)
                            THEN 1 ELSE 0 END) as niederlagen,
                        SUM(CASE WHEN m.spieler1_id = s.id THEN m.satz_score_s1
                                 ELSE m.satz_score_s2 END) as saetze_gewonnen,
                        SUM(CASE WHEN m.spieler1_id = s.id THEN m.satz_score_s2
                                 ELSE m.satz_score_s1 END) as saetze_verloren
                    FROM spieler s
                    JOIN matches m ON s.id = m.spieler1_id OR s.id = m.spieler2_id
                    WHERE m.turnier_id = %s
                    GROUP BY s.id, s.vorname, s.nachname
                ) as stats
                ORDER BY siege DESC, satzdiff DESC
            """
            cursor.execute(query, (turnier_id,))
            rangliste = cursor.fetchall()
            cursor.close()
            return rangliste
        except Error as e:
            print(f"❌ Fehler Rankliste: {e}")
            return []

    def get_match_sets(self, match_id):
        """Lädt die Einzel-Satz-Ergebnisse eines Matches.

        Returns:
            Liste von (set_nummer, punkte_s1, punkte_s2)
        """
        if not MYSQL_AVAILABLE or not self.connection:
            return []
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT set_nummer, punkte_s1, punkte_s2 FROM match_sets WHERE match_id = %s ORDER BY set_nummer",
                (match_id,)
            )
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"❌ Fehler beim Laden der Sätze: {e}")
            return []

    def get_turnier_details(self, turnier_id):
        """Gibt (id, name, erstellt_am, sets_to_win) eines Turniers zurück."""
        if not MYSQL_AVAILABLE or not self.connection:
            return None
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT id, name, erstellt_am, sets_to_win FROM turniere WHERE id = %s",
                (turnier_id,)
            )
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            print(f"❌ Fehler beim Laden des Turniers: {e}")
            return None

    def get_turnier_spieler(self, turnier_id):
        """Gibt alle Spieler zurück, die bereits in diesem Turnier gespielt haben.

        Returns:
            Liste von (id, full_name)
        """
        if not MYSQL_AVAILABLE or not self.connection:
            return []
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT DISTINCT s.id, CONCAT(s.vorname, ' ', s.nachname) as name
                FROM spieler s
                JOIN matches m ON s.id = m.spieler1_id OR s.id = m.spieler2_id
                WHERE m.turnier_id = %s
                ORDER BY name
            """, (turnier_id,))
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"❌ Fehler beim Laden der Turnier-Spieler: {e}")
            return []

    def get_spieler_gesamt_stats(self, turnier_id):
        """Gesamt-Statistik aller Spieler im Turnier über alle ihre Turniere."""
        if not MYSQL_AVAILABLE or not self.connection:
            return []
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT
                    CONCAT(s.vorname, ' ', s.nachname) as name,
                    SUM(CASE
                        WHEN (m.spieler1_id = s.id AND m.satz_score_s1 > m.satz_score_s2)
                          OR (m.spieler2_id = s.id AND m.satz_score_s2 > m.satz_score_s1)
                        THEN 1 ELSE 0 END) as siege_gesamt,
                    SUM(CASE
                        WHEN (m.spieler1_id = s.id AND m.satz_score_s1 < m.satz_score_s2)
                          OR (m.spieler2_id = s.id AND m.satz_score_s2 < m.satz_score_s1)
                        THEN 1 ELSE 0 END) as niederlagen_gesamt,
                    COUNT(DISTINCT m.turnier_id) as anzahl_turniere
                FROM spieler s
                JOIN matches m ON s.id = m.spieler1_id OR s.id = m.spieler2_id
                WHERE s.id IN (
                    SELECT DISTINCT spieler1_id FROM matches WHERE turnier_id = %s
                    UNION
                    SELECT DISTINCT spieler2_id FROM matches WHERE turnier_id = %s
                )
                AND m.turnier_id IS NOT NULL
                GROUP BY s.id, s.vorname, s.nachname
                ORDER BY siege_gesamt DESC
            """
            cursor.execute(query, (turnier_id, turnier_id))
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"❌ Fehler Gesamt-Stats: {e}")
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
        
        # Titel (Dynamic)
        self.title = QLabel("Match Setup")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)
        
        # ===== Match-Modus Auswahl (Radio Buttons) =====
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(15)
        
        lbl_mode = QLabel("Match-Typ:")
        lbl_mode.setStyleSheet("font-size: 22px; color: #888888;")
        mode_layout.addWidget(lbl_mode)
        
        # Button Group für exklusive Auswahl
        self.mode_group = QButtonGroup(self)
        self.mode_group.idClicked.connect(self.on_mode_changed)
        
        # Die 5 gewünschten Modi als Radio Buttons
        modes = [
            (0, "Schnell"),      # Schnelles Spiel
            (1, "Best of 3"),    # Best of 3
            (2, "Best of 5"),    # Best of 5
            (3, "Best of 7"),    # Best of 7
            (4, "Turnier")       # Turnier
        ]
        
        radio_style = """
            QRadioButton { 
                font-size: 20px; 
                color: #ffffff; 
                spacing: 8px;
                padding: 10px;
                border: 1px solid transparent;
                border-radius: 5px;
            }
            QRadioButton:hover {
                background-color: #1a1a2e;
                border: 1px solid #0f3460;
            }
            QRadioButton::indicator { 
                width: 24px; 
                height: 24px; 
            }
            QRadioButton::indicator:checked { 
                background-color: #00d9ff; 
                border: 2px solid #00d9ff; 
                border-radius: 12px; 
            }
            QRadioButton::indicator:unchecked { 
                background-color: #16213e; 
                border: 2px solid #0f3460; 
                border-radius: 12px; 
            }
        """
        
        for mode_id, text in modes:
            rb = QRadioButton(text)
            rb.setStyleSheet(radio_style)
            self.mode_group.addButton(rb, mode_id)
            mode_layout.addWidget(rb)
            
            if mode_id == 0: # Default: Schnelles Spiel
                rb.setChecked(True)
        
        mode_layout.addStretch()
        layout.addLayout(mode_layout)
        
        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setStyleSheet("background-color: #0f3460; max-height: 2px;")
        layout.addWidget(separator1)
        
        # ===== Turnier-Auswahl (Versteckt, nur bei "Turnier") =====
        self.turnier_container = QWidget()
        turnier_layout = QHBoxLayout(self.turnier_container)
        turnier_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_turnier = QLabel("Turnier:")
        lbl_turnier.setStyleSheet("font-size: 22px; color: #00d9ff;")
        turnier_layout.addWidget(lbl_turnier)
        
        self.combo_turnier = QComboBox()
        self.combo_turnier.setMinimumHeight(55)
        self.combo_turnier.setStyleSheet("""
            QComboBox { background-color: #16213e; color: #ffffff; border: 2px solid #0f3460; border-radius: 10px; padding: 10px; font-size: 18px; }
            QComboBox QAbstractItemView { background-color: #16213e; color: #ffffff; selection-background-color: #00d9ff; selection-color: #1a1a2e; }
        """)
        turnier_layout.addWidget(self.combo_turnier, 1)
        
        btn_new_turnier = QPushButton("+ Neu")
        btn_new_turnier.setMinimumHeight(55)
        btn_new_turnier.clicked.connect(self.on_new_turnier)
        turnier_layout.addWidget(btn_new_turnier)
        
        layout.addWidget(self.turnier_container)
        
        # ===== Spieler Eingabe Container =====
        self.player_input_container = QWidget()
        player_layout = QVBoxLayout(self.player_input_container)
        player_layout.setContentsMargins(0, 10, 0, 10)
        player_layout.setSpacing(10)
        
        lbl_player1 = QLabel("Spieler 1 (Links)")
        lbl_player1.setStyleSheet("font-size: 22px; color: #00d9ff;")
        player_layout.addWidget(lbl_player1)
        
        self.input_player1 = QLineEdit()
        self.input_player1.setPlaceholderText("Name eingeben oder suchen...")
        self.input_player1.setMinimumHeight(55)
        player_layout.addWidget(self.input_player1)
        
        self.vs_label = QLabel("VS")
        self.vs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vs_label.setStyleSheet("font-size: 32px; color: #e94560; font-weight: bold; margin: 10px 0;")
        player_layout.addWidget(self.vs_label)
        
        lbl_player2 = QLabel("Spieler 2 (Rechts)")
        lbl_player2.setStyleSheet("font-size: 22px; color: #00d9ff;")
        player_layout.addWidget(lbl_player2)
        
        self.input_player2 = QLineEdit()
        self.input_player2.setPlaceholderText("Name eingeben oder suchen...")
        self.input_player2.setMinimumHeight(55)
        player_layout.addWidget(self.input_player2)
        
        layout.addWidget(self.player_input_container)

        # ===== Quick Match Info Label (Nur sichtbar bei Schnelles Spiel) =====
        self.quick_label = QLabel("Starte das Spiel")
        self.quick_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quick_label.setStyleSheet("font-size: 96px; color: #00d9ff; font-weight: bold; margin: 40px;")
        self.quick_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.quick_label, 1)
        
        # Input Settings
        self.input_player1.setReadOnly(True)
        self.input_player2.setReadOnly(True)
        self.input_player1.mousePressEvent = lambda e: self.open_keyboard(self.input_player1, "Spieler 1")
        self.input_player2.mousePressEvent = lambda e: self.open_keyboard(self.input_player2, "Spieler 2")
        
        layout.addStretch()
        
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
        
        self.setLayout(layout)
        
        # Initiale Sichtbarkeit setzen
        self.on_mode_changed()
    
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
            raw_players = self.main_window.db.get_spieler()
            player_names = [f"{p[1]} {p[2]}" for p in raw_players]
            completer = QCompleter(player_names)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            self.input_player1.setCompleter(completer)
            self.input_player2.setCompleter(completer)

    def on_mode_changed(self):
        """Passt UI basierend auf Auswahl an."""
        index = self.mode_group.checkedId()
        if index == -1: index = 0 # Fallback
        
        # Titel aktualisieren
        mode_names = {
            0: "Schnelles Spiel",
            1: "Best of 3",
            2: "Best of 5",
            3: "Best of 7",
            4: "Turnier Modus"
        }
        self.title.setText(mode_names.get(index, "Match Setup"))

        # 0: Schnelles Spiel, 1: Best of 3, 2: Best of 5, 3: Best of 7, 4: Turnier
        
        is_quick = (index == 0)
        is_turnier = (index == 4)
        
        # Schnelles Spiel: Keine Namenseingabe
        # Schnelles Spiel: Keine Namenseingabe, dafür Info-Label
        self.player_input_container.setVisible(not is_quick)
        self.quick_label.setVisible(is_quick)
        
        # Turnier: Extra Dropdown anzeigen
        self.turnier_container.setVisible(is_turnier)
        if is_turnier:
            self.load_turniere()
    
    def load_turniere(self):
        self.combo_turnier.clear()
        if self.main_window and self.main_window.db:
            self.turniere = self.main_window.db.get_turniere()
            for turnier in self.turniere:
                # turnier = (id, name, datum, sets_to_win)
                # Falls sets_to_win fehlt (altes Schema), Default 3
                sets = 3
                if len(turnier) > 3:
                    sets = turnier[3]
                    
                turnier_id = turnier[0]
                turnier_name = turnier[1]
                
                # Speichere sets_to_win in den Item-Daten als Tuple (id, sets)
                self.combo_turnier.addItem(turnier_name, (turnier_id, sets))
    
    def on_new_turnier(self):
        if not self.main_window:
            return

        def on_created(tid, name):
            self.load_turniere()
            # Neu erstelltes Turnier automatisch auswählen
            for i in range(self.combo_turnier.count()):
                data = self.combo_turnier.itemData(i)  # (id, sets)
                if data and data[0] == tid:
                    self.combo_turnier.setCurrentIndex(i)
                    break

        self.main_window.show_neu_turnier_page(return_index=1, on_created_callback=on_created)
    
    def clear_inputs(self):
        self.input_player1.clear()
        self.input_player2.clear()
        # Reset auf Default (Schnelles Spiel)
        btn = self.mode_group.button(0)
        if btn: btn.setChecked(True)
        self.on_mode_changed()
    
    def on_back(self):
        if self.main_window:
            self.main_window.show_start_menu()
    
    def on_start(self):
        mode_index = self.mode_group.checkedId()
        if mode_index == -1: mode_index = 0
        
        # Modus Logik
        # 0: Schnelles Spiel -> 1 Satz
        # 1: Best of 3 -> 2 Sätze
        # 2: Best of 5 -> 3 Sätze
        # 3: Best of 7 -> 4 Sätze
        # 4: Turnier
        
        sets_to_win = 1
        if mode_index == 1: sets_to_win = 2
        elif mode_index == 2: sets_to_win = 3
        elif mode_index == 3: sets_to_win = 4
        elif mode_index == 4: sets_to_win = 3 # Turnier Standard, oder aus DB laden?
        
        player1_name = ""
        player2_name = ""
        
        # Schnelles Spiel
        if mode_index == 0:
            player1_name = "Spieler Links"
            player2_name = "Spieler Rechts"
        else:
            # Alle anderen Modi benötigen Namen
            player1_name = self.input_player1.text().strip()
            player2_name = self.input_player2.text().strip()
            
            if not player1_name or not player2_name:
                show_custom_info_dialog(self, "Fehler", "Bitte gib beide Spielernamen ein!")
                return
            
            if player1_name.lower() == player2_name.lower():
                show_custom_info_dialog(self, "Fehler", "Die Spielernamen müssen unterschiedlich sein!")
                return
        
        turnier_id = None
        turnier_name = None
        if mode_index == 4: # Turnier
            if self.combo_turnier.count() == 0:
                show_custom_info_dialog(self, "Fehler", "Bitte wähle ein Turnier aus!")
                return
            
            # Data ist jetzt (turnier_id, sets_to_win)
            data = self.combo_turnier.currentData()
            if data:
                turnier_id = data[0]
                sets_to_win = data[1] # HIER: Lade Regel aus Turnier
                turnier_name = self.combo_turnier.currentText()
        
        if self.main_window:
            self.main_window.current_turnier_id = turnier_id
            self.main_window.current_turnier_name = turnier_name
            self.main_window.page_scoreboard.turnier_id = turnier_id
            # Hier übergeben wir sets_to_win an reset_match
            self.main_window.page_scoreboard.reset_match(None, player1_name, None, player2_name, sets_to_win=sets_to_win)
            self.main_window.stack.setCurrentIndex(4)
            self.main_window.page_scoreboard.setFocus()


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
                turnier_id, name, erstellt_am, sets_to_win = turnier
                sets_label = f"Bo{sets_to_win * 2 - 1}"
                datum_str = str(erstellt_am)[:10] if erstellt_am else ""
                item = QListWidgetItem(f"{name}  |  {sets_label}  |  {datum_str}")
                item.setData(Qt.ItemDataRole.UserRole, turnier_id)
                self.turnier_list.addItem(item)
    
    def on_back(self):
        if self.main_window:
            self.main_window.show_start_menu()
    
    def on_new_turnier(self):
        if not self.main_window:
            return

        def on_created(tid, name):
            self.load_turniere()

        self.main_window.show_neu_turnier_page(return_index=2, on_created_callback=on_created)
    
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
    
    # ── shared stylesheet fragments ────────────────────────────────────────
    _SECTION_HEADER_SS = """
        QWidget { background-color: #0d1b2e; border-radius: 6px; }
        QLabel  { color: #00d9ff; font-size: 13px; font-weight: bold;
                  letter-spacing: 1px; background: transparent; }
    """
    _MATCH_TABLE_SS = """
        QTableWidget {
            background-color: transparent;
            border: none;
            outline: 0;
            gridline-color: transparent;
        }
        QTableWidget::item {
            border-bottom: 1px solid #0d1b2e;
            padding: 0px 6px;
        }
        QTableWidget::item:selected {
            background-color: #0f3460;
        }
        QScrollBar:vertical {
            background: #12192b; width: 6px; border-radius: 3px;
        }
        QScrollBar::handle:vertical {
            background: #0f3460; border-radius: 3px; min-height: 20px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
    """
    _RANK_TABLE_SS = """
        QTableWidget {
            background-color: transparent;
            border: none;
            outline: 0;
            gridline-color: transparent;
        }
        QHeaderView::section {
            background-color: #0d1b2e;
            color: #555e7a;
            border: none;
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 1px;
            padding: 6px 4px;
            text-transform: uppercase;
        }
        QTableWidget::item {
            border-bottom: 1px solid #0d1b2e;
            padding: 0px 4px;
        }
        QScrollBar:vertical {
            background: #12192b; width: 6px; border-radius: 3px;
        }
        QScrollBar::handle:vertical {
            background: #0f3460; border-radius: 3px; min-height: 20px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
    """
    _STATS_TABLE_SS = """
        QTableWidget {
            background-color: transparent;
            border: none;
            outline: 0;
            gridline-color: transparent;
        }
        QHeaderView::section {
            background-color: #0d1b2e;
            color: #555e7a;
            border: none;
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 1px;
            padding: 6px 4px;
        }
        QTableWidget::item {
            border-bottom: 1px solid #0d1b2e;
            padding: 0px 6px;
        }
    """
    _CARD_SS   = "background-color: #12192b; border-radius: 10px;"
    _ROW_H_MATCH = 52
    _ROW_H_RANK  = 46

    def _make_section_header(self, left_text, right_text=""):
        bar = QWidget()
        bar.setFixedHeight(36)
        bar.setStyleSheet(self._SECTION_HEADER_SS)
        row = QHBoxLayout(bar)
        row.setContentsMargins(10, 0, 10, 0)
        lbl_l = QLabel(left_text.upper())
        row.addWidget(lbl_l)
        row.addStretch()
        if right_text:
            lbl_r = QLabel(right_text)
            lbl_r.setStyleSheet("color: #3a4460; font-size: 12px; font-weight: normal; background: transparent;")
            row.addWidget(lbl_r)
        return bar

    def _card_wrap(self, inner_widget):
        """Wraps a widget in a card (rounded dark box)."""
        card = QWidget()
        card.setStyleSheet(self._CARD_SS)
        l = QVBoxLayout(card)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(0)
        l.addWidget(inner_widget)
        return card

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 16, 20, 16)

        # ── Title ─────────────────────────────────────────────────────────
        self.title_label = QLabel("Turnier")
        self.title_label.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #00d9ff;"
        )
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # ── Main two-column area ───────────────────────────────────────────
        content = QHBoxLayout()
        content.setSpacing(14)

        # ══ LEFT: Match list ══════════════════════════════════════════════
        left_col = QVBoxLayout()
        left_col.setSpacing(4)
        left_col.addWidget(self._make_section_header("Ergebnisse", "Antippen = Satz-Detail"))

        self.match_table = QTableWidget()
        self.match_table.setColumnCount(4)
        # 0: date  1: player1  2: score  3: player2
        self.match_table.horizontalHeader().setVisible(False)
        self.match_table.verticalHeader().setVisible(False)
        self.match_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.match_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.match_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.match_table.setShowGrid(False)
        self.match_table.setCursor(Qt.CursorShape.PointingHandCursor)
        self.match_table.setStyleSheet(self._MATCH_TABLE_SS)
        self.match_table.cellClicked.connect(self.on_match_double_clicked)
        left_col.addWidget(self._card_wrap(self.match_table), 1)

        left_container = QWidget()
        left_container.setLayout(left_col)
        content.addWidget(left_container, 55)

        # ══ RIGHT: Ranking ════════════════════════════════════════════════
        right_col = QVBoxLayout()
        right_col.setSpacing(4)
        right_col.addWidget(self._make_section_header("Rangliste"))

        self.rank_table = QTableWidget()
        self.rank_table.setColumnCount(6)
        self.rank_table.setHorizontalHeaderLabels(["#", "Spieler", "S", "N", "Sätze", "±"])
        self.rank_table.horizontalHeader().setVisible(True)
        self.rank_table.verticalHeader().setVisible(False)
        self.rank_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for col in (0, 2, 3, 4, 5):
            self.rank_table.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.ResizeToContents
            )
        self.rank_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.rank_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.rank_table.setShowGrid(False)
        self.rank_table.setStyleSheet(self._RANK_TABLE_SS)
        right_col.addWidget(self._card_wrap(self.rank_table), 1)

        right_container = QWidget()
        right_container.setLayout(right_col)
        content.addWidget(right_container, 45)

        layout.addLayout(content, 1)

        # ── Stats strip ───────────────────────────────────────────────────
        stats_header = self._make_section_header("Spieler-Gesamtstatistik")
        layout.addWidget(stats_header)

        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(4)
        self.stats_table.setHorizontalHeaderLabels(["Spieler", "Siege", "Niederlagen", "Turniere"])
        self.stats_table.verticalHeader().setVisible(False)
        self.stats_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in (1, 2, 3):
            self.stats_table.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.ResizeToContents
            )
        self.stats_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.stats_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.stats_table.setShowGrid(False)
        self.stats_table.setMaximumHeight(self._ROW_H_RANK * 4 + 30)
        self.stats_table.setStyleSheet(self._STATS_TABLE_SS)
        layout.addWidget(self._card_wrap(self.stats_table))

        # ── Buttons ───────────────────────────────────────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        btn_back = QPushButton("← Zurück")
        btn_back.setMinimumHeight(62)
        btn_back.clicked.connect(self.on_back)
        btn_layout.addWidget(btn_back)

        btn_play = QPushButton("Match spielen")
        btn_play.setObjectName("primary")
        btn_play.setMinimumHeight(62)
        btn_play.clicked.connect(self.on_play_match)
        btn_layout.addWidget(btn_play)

        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    # ── colour constants ───────────────────────────────────────────────────
    _C_WINNER  = "#ffffff"   # white + bold
    _C_LOSER   = "#4a5570"   # muted blue-grey
    _C_SCORE_W = "#00d9ff"   # cyan
    _C_SCORE_L = "#4a5570"
    _C_DATE    = "#3a4460"
    _C_ROW_ODD = "#12192b"
    _C_ROW_EVN = "#0e1525"
    _MEDALS    = {0: "🥇", 1: "🥈", 2: "🥉"}

    def _make_item(self, text, align=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                   fg=None, bold=False, bg=None):
        item = QTableWidgetItem(text)
        item.setTextAlignment(align)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        if fg:
            item.setForeground(QColor(fg))
        if bold:
            f = QFont()
            f.setBold(True)
            item.setFont(f)
        if bg:
            item.setBackground(QColor(bg))
        return item

    def _set_row_bg(self, table, row, color):
        brush = QBrush(QColor(color))
        for col in range(table.columnCount()):
            item = table.item(row, col)
            if item:
                item.setBackground(brush)

    def load_turnier(self, turnier_id, turnier_name):
        self.turnier_id = turnier_id
        self.turnier_name = turnier_name
        self.title_label.setText(turnier_name)

        if not (self.main_window and self.main_window.db):
            return

        CENTER = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter
        RIGHT  = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight
        LEFT   = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft

        # ── Match-Historie ────────────────────────────────────────────────
        matches = self.main_window.db.get_turnier_matches(turnier_id)
        self.match_table.setRowCount(len(matches))

        # Column widths: date=88 | p1=stretch | score=68 | p2=stretch
        self.match_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.match_table.setColumnWidth(0, 88)
        self.match_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.match_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.match_table.setColumnWidth(2, 68)
        self.match_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        for row, match in enumerate(matches):
            match_id, spieler1, spieler2, score1, score2, datum = match
            row_bg = self._C_ROW_ODD if row % 2 == 0 else self._C_ROW_EVN
            p1_won = score1 > score2

            # Date column (col 0)
            datum_str = str(datum)[5:16] if datum else "-"   # "MM-DD HH:MM"
            date_item = self._make_item(datum_str, CENTER, fg=self._C_DATE, bg=row_bg)
            date_item.setData(Qt.ItemDataRole.UserRole, match_id)
            self.match_table.setItem(row, 0, date_item)

            # Player 1 (col 1) — right-aligned
            p1_item = self._make_item(
                spieler1, RIGHT,
                fg=self._C_WINNER if p1_won else self._C_LOSER,
                bold=p1_won, bg=row_bg
            )
            self.match_table.setItem(row, 1, p1_item)

            # Score (col 2) — centre, winner side cyan
            score_text = f"{score1}  :  {score2}"
            score_item = self._make_item(score_text, CENTER, fg=self._C_SCORE_W, bold=True, bg=row_bg)
            self.match_table.setItem(row, 2, score_item)

            # Player 2 (col 3) — left-aligned
            p2_item = self._make_item(
                spieler2, LEFT,
                fg=self._C_WINNER if not p1_won else self._C_LOSER,
                bold=not p1_won, bg=row_bg
            )
            self.match_table.setItem(row, 3, p2_item)

            self.match_table.setRowHeight(row, self._ROW_H_MATCH)

        # ── Rangliste ─────────────────────────────────────────────────────
        rangliste = self.main_window.db.get_rangliste(turnier_id)
        self.rank_table.setRowCount(len(rangliste))

        for row, eintrag in enumerate(rangliste):
            name, siege, niederlagen, saetze_gew, saetze_verl, satzdiff = eintrag
            row_bg = self._C_ROW_ODD if row % 2 == 0 else self._C_ROW_EVN

            medal = self._MEDALS.get(row, "")
            rank_text = f"{medal} {row + 1}" if medal else f"  {row + 1}"
            self.rank_table.setItem(row, 0, self._make_item(rank_text, CENTER, fg="#888888", bg=row_bg))

            name_fg = "#ffffff" if row == 0 else "#cccccc"
            self.rank_table.setItem(row, 1, self._make_item(name, LEFT, fg=name_fg, bold=(row == 0), bg=row_bg))

            self.rank_table.setItem(row, 2, self._make_item(str(siege), CENTER, fg="#00d9ff", bold=True, bg=row_bg))
            self.rank_table.setItem(row, 3, self._make_item(str(niederlagen), CENTER, fg=self._C_LOSER, bg=row_bg))
            self.rank_table.setItem(row, 4, self._make_item(f"{saetze_gew}:{saetze_verl}", CENTER, fg="#888888", bg=row_bg))

            diff_str = f"+{satzdiff}" if satzdiff > 0 else str(satzdiff)
            diff_fg = "#00c853" if satzdiff > 0 else ("#e94560" if satzdiff < 0 else "#888888")
            self.rank_table.setItem(row, 5, self._make_item(diff_str, CENTER, fg=diff_fg, bold=(satzdiff != 0), bg=row_bg))

            self.rank_table.setRowHeight(row, self._ROW_H_RANK)

        # ── Gesamt-Statistik ──────────────────────────────────────────────
        gesamt = self.main_window.db.get_spieler_gesamt_stats(turnier_id)
        self.stats_table.setRowCount(len(gesamt))

        for row, eintrag in enumerate(gesamt):
            name, siege_g, niederlagen_g, anz_turniere = eintrag
            row_bg = self._C_ROW_ODD if row % 2 == 0 else self._C_ROW_EVN
            self.stats_table.setItem(row, 0, self._make_item(name, LEFT, fg="#cccccc", bg=row_bg))
            self.stats_table.setItem(row, 1, self._make_item(str(siege_g), CENTER, fg="#00d9ff", bold=True, bg=row_bg))
            self.stats_table.setItem(row, 2, self._make_item(str(niederlagen_g), CENTER, fg=self._C_LOSER, bg=row_bg))
            self.stats_table.setItem(row, 3, self._make_item(str(anz_turniere), CENTER, fg="#888888", bg=row_bg))
            self.stats_table.setRowHeight(row, self._ROW_H_RANK)
    
    def on_match_double_clicked(self, row, col):
        """Zeigt Satz-Detailansicht für das angeklickte Match."""
        date_item = self.match_table.item(row, 0)   # match_id stored here
        if not date_item:
            return
        match_id = date_item.data(Qt.ItemDataRole.UserRole)
        p1_item = self.match_table.item(row, 1)
        p2_item = self.match_table.item(row, 3)
        score_item = self.match_table.item(row, 2)
        spieler1 = p1_item.text().strip() if p1_item else ""
        spieler2 = p2_item.text().strip() if p2_item else ""
        ergebnis = score_item.text().strip() if score_item else ""
        self.show_match_detail(match_id, spieler1, spieler2, ergebnis)

    def show_match_detail(self, match_id, spieler1, spieler2, ergebnis):
        """Öffnet einen Dialog mit den Einzel-Satz-Ergebnissen eines Matches."""
        if not self.main_window or not self.main_window.db:
            return
        set_data = self.main_window.db.get_match_sets(match_id)

        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        dialog.setMinimumWidth(520)
        dialog.setStyleSheet("""
            QDialog { background-color: #0e1525; border: 2px solid #0f3460; border-radius: 14px; }
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # ── Header bar ────────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(56)
        header.setStyleSheet("background-color: #0d1b2e; border-radius: 12px 12px 0 0;")
        h_row = QHBoxLayout(header)
        h_row.setContentsMargins(20, 0, 20, 0)
        lbl_title = QLabel(f"{spieler1}   {ergebnis}   {spieler2}")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_row.addWidget(lbl_title)
        layout.addWidget(header)

        # ── Set rows ──────────────────────────────────────────────────────
        body = QWidget()
        body.setStyleSheet("background-color: #0e1525;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 12, 20, 12)
        body_layout.setSpacing(0)

        CENTER = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter
        RIGHT  = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight
        LEFT   = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft

        if set_data:
            table = QTableWidget()
            table.setColumnCount(3)
            table.horizontalHeader().setVisible(False)
            table.verticalHeader().setVisible(False)
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
            table.setShowGrid(False)
            table.setStyleSheet("""
                QTableWidget { background: transparent; border: none; }
                QTableWidget::item { border-bottom: 1px solid #0d1b2e; padding: 4px 8px; }
            """)
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
            table.setColumnWidth(1, 80)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            table.setRowCount(len(set_data))

            # column header row (fake — first row with labels)
            # Build a proper header widget above
            hdr_w = QWidget()
            hdr_w.setStyleSheet("background: #0d1b2e; border-radius: 6px;")
            hdr_l = QHBoxLayout(hdr_w)
            hdr_l.setContentsMargins(8, 4, 8, 4)
            for txt, stretch in [(spieler1, 1), ("", 0), (spieler2, 1)]:
                lbl = QLabel(txt)
                lbl.setStyleSheet("color: #555e7a; font-size: 13px; font-weight: bold; letter-spacing: 1px;")
                if txt == spieler1:
                    lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                elif txt == spieler2:
                    lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                else:
                    lbl.setFixedWidth(80)
                    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                hdr_l.addWidget(lbl, stretch)
            body_layout.addWidget(hdr_w)
            body_layout.addSpacing(4)

            for row_idx, (set_nr, p1, p2) in enumerate(set_data):
                row_bg = "#12192b" if row_idx % 2 == 0 else "#0e1525"
                p1_won = p1 > p2

                bold_f = QFont(); bold_f.setBold(True)
                norm_f = QFont(); norm_f.setBold(False)

                # P1
                i1 = QTableWidgetItem(str(p1))
                i1.setTextAlignment(RIGHT)
                i1.setForeground(QColor("#ffffff" if p1_won else "#4a5570"))
                i1.setFont(bold_f if p1_won else norm_f)
                i1.setBackground(QColor(row_bg))
                table.setItem(row_idx, 0, i1)

                # Set label centre
                i_set = QTableWidgetItem(f"Satz {set_nr}")
                i_set.setTextAlignment(CENTER)
                i_set.setForeground(QColor("#3a4460"))
                i_set.setBackground(QColor(row_bg))
                table.setItem(row_idx, 1, i_set)

                # P2
                i2 = QTableWidgetItem(str(p2))
                i2.setTextAlignment(LEFT)
                i2.setForeground(QColor("#ffffff" if not p1_won else "#4a5570"))
                i2.setFont(bold_f if not p1_won else norm_f)
                i2.setBackground(QColor(row_bg))
                table.setItem(row_idx, 2, i2)

                table.setRowHeight(row_idx, 46)

            table.setFixedHeight(len(set_data) * 46 + 4)
            body_layout.addWidget(table)
        else:
            lbl = QLabel("Keine Satz-Details verfügbar.")
            lbl.setStyleSheet("color: #4a5570; font-size: 15px; padding: 20px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            body_layout.addWidget(lbl)

        layout.addWidget(body)

        # ── Close button ──────────────────────────────────────────────────
        btn_close = QPushButton("Schließen")
        btn_close.setMinimumHeight(52)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #0d1b2e; color: #00d9ff;
                border: none; border-radius: 0 0 12px 12px;
                font-size: 16px; font-weight: bold;
            }
            QPushButton:pressed { background-color: #0f3460; }
        """)
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close)

        dialog.exec()

    def on_back(self):
        if self.main_window:
            self.main_window.show_turnier_list()

    def on_play_match(self):
        if self.main_window:
            self.main_window.start_turnier_match(self.turnier_id, self.turnier_name)


# ==================== SEITE 5: TURNIER MATCH SETUP ====================
class TurnierMatchSetupPage(QWidget):
    """Spielerauswahl für ein Turnier-Match aus den bereits erfassten Spielern."""

    _STYLE_P1 = """
        QPushButton {
            background-color: #00d9ff; color: #1a1a2e;
            border: none; border-radius: 12px;
            font-size: 22px; font-weight: bold; padding: 10px;
        }
    """
    _STYLE_P2 = """
        QPushButton {
            background-color: #e94560; color: #ffffff;
            border: none; border-radius: 12px;
            font-size: 22px; font-weight: bold; padding: 10px;
        }
    """
    _STYLE_DEFAULT = """
        QPushButton {
            background-color: #16213e; color: #ffffff;
            border: 2px solid #0f3460; border-radius: 12px;
            font-size: 22px; padding: 10px;
        }
        QPushButton:pressed { background-color: #0f3460; }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.turnier_id = None
        self.turnier_name = ""
        self.sets_to_win = 3
        self.player1_name = None
        self.player2_name = None
        self._player_buttons = {}
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("TurnierMatchSetupPage")
        self.setStyleSheet("#TurnierMatchSetupPage { background-color: #1a1a2e; }")

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(50, 30, 50, 30)

        # ===== Titel =====
        self.title_label = QLabel("Match starten")
        self.title_label.setStyleSheet("font-size: 26px; color: #00d9ff; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # ===== Auswahlzeile: P1 | VS | P2 =====
        sel_layout = QHBoxLayout()
        sel_layout.setSpacing(15)

        p1_col = QVBoxLayout()
        lbl_p1_title = QLabel("Spieler 1")
        lbl_p1_title.setStyleSheet("font-size: 18px; color: #00d9ff; font-weight: bold;")
        lbl_p1_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        p1_col.addWidget(lbl_p1_title)
        self.lbl_p1 = QLabel("---")
        self.lbl_p1.setMinimumHeight(58)
        self.lbl_p1.setStyleSheet("""
            font-size: 22px; color: #1a1a2e; font-weight: bold;
            background-color: #00d9ff; border-radius: 12px; padding: 10px;
        """)
        self.lbl_p1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        p1_col.addWidget(self.lbl_p1)
        sel_layout.addLayout(p1_col, 1)

        vs = QLabel("VS")
        vs.setStyleSheet("font-size: 28px; color: #e94560; font-weight: bold;")
        vs.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vs.setFixedWidth(55)
        sel_layout.addWidget(vs)

        p2_col = QVBoxLayout()
        lbl_p2_title = QLabel("Spieler 2")
        lbl_p2_title.setStyleSheet("font-size: 18px; color: #e94560; font-weight: bold;")
        lbl_p2_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        p2_col.addWidget(lbl_p2_title)
        self.lbl_p2 = QLabel("---")
        self.lbl_p2.setMinimumHeight(58)
        self.lbl_p2.setStyleSheet("""
            font-size: 22px; color: #ffffff; font-weight: bold;
            background-color: #e94560; border-radius: 12px; padding: 10px;
        """)
        self.lbl_p2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        p2_col.addWidget(self.lbl_p2)
        sel_layout.addLayout(p2_col, 1)

        layout.addLayout(sel_layout)

        # ===== Hinweis =====
        hint = QLabel("1. Spieler 1 antippen  →  2. Spieler 2 antippen  ·  Erneut antippen = Abwählen")
        hint.setStyleSheet("font-size: 15px; color: #555555;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        # ===== Spieler-Grid =====
        self.players_container = QWidget()
        self.players_grid = QGridLayout(self.players_container)
        self.players_grid.setSpacing(12)
        layout.addWidget(self.players_container, 1)

        # ===== Buttons =====
        btn_row = QHBoxLayout()
        btn_row.setSpacing(20)

        btn_back = QPushButton("← Zurück")
        btn_back.setMinimumHeight(70)
        btn_back.setStyleSheet("""
            QPushButton {
                background-color: #16213e; color: #ffffff;
                border: 2px solid #0f3460; border-radius: 15px; font-size: 20px;
            }
            QPushButton:pressed { background-color: #0f3460; }
        """)
        btn_back.clicked.connect(self._on_back)
        btn_row.addWidget(btn_back)

        self.btn_start = QPushButton("Match Starten")
        self.btn_start.setMinimumHeight(70)
        self.btn_start.setEnabled(False)
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #00d9ff; color: #1a1a2e;
                border: none; border-radius: 15px; font-size: 20px; font-weight: bold;
            }
            QPushButton:disabled {
                background-color: #16213e; color: #444444; border: 2px solid #0f3460;
            }
            QPushButton:pressed { background-color: #00b8d4; }
        """)
        self.btn_start.clicked.connect(self._on_start)
        btn_row.addWidget(self.btn_start)

        layout.addLayout(btn_row)

    def load(self, turnier_id, turnier_name):
        self.turnier_id = turnier_id
        self.turnier_name = turnier_name
        self.player1_name = None
        self.player2_name = None
        self._player_buttons = {}

        # Fetch sets_to_win from DB
        self.sets_to_win = 3
        if self.main_window and self.main_window.db:
            details = self.main_window.db.get_turnier_details(turnier_id)
            if details:
                self.sets_to_win = details[3] or 3

        display = turnier_name[:40] + "..." if len(turnier_name) > 40 else turnier_name
        self.title_label.setText(f"Match starten  ·  {display}")
        self._update_selection_display()
        self._load_players()

    def _load_players(self):
        # Clear old buttons
        while self.players_grid.count():
            item = self.players_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._player_buttons = {}

        if not self.main_window or not self.main_window.db:
            return

        players = self.main_window.db.get_turnier_spieler(self.turnier_id)
        cols = 3
        for i, (pid, name) in enumerate(players):
            btn = QPushButton(name)
            btn.setMinimumHeight(70)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(self._STYLE_DEFAULT)
            btn.clicked.connect(lambda checked, n=name: self._on_player_tap(n))
            self._player_buttons[name] = btn
            self.players_grid.addWidget(btn, i // cols, i % cols)

        self.btn_start.setEnabled(False)

    def _on_player_tap(self, name):
        if self.player1_name == name:
            self.player1_name = None
        elif self.player2_name == name:
            self.player2_name = None
        elif self.player1_name is None:
            self.player1_name = name
        else:
            self.player2_name = name

        self._update_selection_display()
        self._update_button_styles()
        self.btn_start.setEnabled(
            self.player1_name is not None and self.player2_name is not None
        )

    def _update_selection_display(self):
        self.lbl_p1.setText(self.player1_name or "---")
        self.lbl_p2.setText(self.player2_name or "---")

    def _update_button_styles(self):
        for name, btn in self._player_buttons.items():
            if name == self.player1_name:
                btn.setStyleSheet(self._STYLE_P1)
            elif name == self.player2_name:
                btn.setStyleSheet(self._STYLE_P2)
            else:
                btn.setStyleSheet(self._STYLE_DEFAULT)

    def _on_back(self):
        if self.main_window:
            self.main_window.show_turnier_detail(self.turnier_id, self.turnier_name)

    def _on_start(self):
        if not self.player1_name or not self.player2_name:
            return
        if self.main_window:
            self.main_window.current_turnier_id = self.turnier_id
            self.main_window.current_turnier_name = self.turnier_name
            self.main_window.page_scoreboard.turnier_id = self.turnier_id
            self.main_window.page_scoreboard.reset_match(
                None, self.player1_name,
                None, self.player2_name,
                sets_to_win=self.sets_to_win
            )
            self.main_window.stack.setCurrentIndex(4)  # ScoreboardPage
            self.main_window.page_scoreboard.setFocus()


# ==================== SEITE 6: SCOREBOARD ====================
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
        self.sets1 = 0
        self.sets2 = 0
        self.sets_to_win = 3  # Standard: Best of 5 (3 Gewinnsätze)
        self.turnier_id = None
        self.set_scores = []  # Liste von (punkte_s1, punkte_s2) je gewonnenem Satz

        # Aufschlag-Tracking: 1 = Spieler 1, 2 = Spieler 2
        self.server = 1
        self.initial_server = 1
        
        # Konfetti-Overlays
        self.confetti_overlay1 = None
        self.confetti_overlay2 = None

        self.setup_ui()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(100, self.setFocus)

    def keyPressEvent(self, event):
        """Pfeiltasten/Presenter: Rechts = Spieler 2, Links = Spieler 1."""
        key = event.key()
        if key in (Qt.Key.Key_Right, Qt.Key.Key_PageDown):
            self.add_point(2)
        elif key in (Qt.Key.Key_Left, Qt.Key.Key_PageUp):
            self.add_point(1)
        else:
            super().keyPressEvent(event)

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
    
    def reset_match(self, player1_id, player1_name, player2_id, player2_name, sets_to_win=3):
        self.player1_id = player1_id
        self.player1_name = player1_name
        self.player2_id = player2_id
        self.player2_name = player2_name
        self.sets_to_win = sets_to_win

        self.score1 = 0
        self.score2 = 0
        self.sets1 = 0
        self.sets2 = 0
        self.history = []
        self.set_scores = []

        # Satz-Anzeigen nur bei Mehratz-Modi zeigen
        show_sets = sets_to_win > 1
        self.lbl_sets1.setVisible(show_sets)
        self.lbl_sets2.setVisible(show_sets)

        # Aufschlag-Auswahl anzeigen
        self.choose_initial_server()
        self.update_display()
    
    def choose_initial_server(self):
        """Zeigt Dialog zur Auswahl des ersten Aufschlägers."""
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        dialog.setStyleSheet("""
            QDialog { background-color: #1a1a2e; border: 3px solid #00d9ff; border-radius: 15px; }
        """)

        def key_press(event: QKeyEvent):
            if event.key() == Qt.Key.Key_Right:
                dialog.accept()
            elif event.key() == Qt.Key.Key_Left:
                dialog.reject()
            else:
                QDialog.keyPressEvent(dialog, event)
        dialog.keyPressEvent = key_press

        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 40)

        lbl = QLabel("Wer hat Aufschlag?")
        lbl.setStyleSheet("color: white; font-size: 26px; font-weight: bold; background: transparent; border: none;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)

        btn_p1 = QPushButton(self.player1_name)
        btn_p1.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_p1.setMinimumHeight(60)
        btn_p1.setStyleSheet("""
            QPushButton { background-color: #16213e; color: white; border: 2px solid #00d9ff; border-radius: 10px; font-size: 20px; min-width: 140px; min-height: 50px; }
            QPushButton:hover { background-color: #00d9ff; color: #1a1a2e; }
        """)
        btn_p1.clicked.connect(dialog.accept)
        btn_layout.addWidget(btn_p1)

        btn_p2 = QPushButton(self.player2_name)
        btn_p2.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_p2.setMinimumHeight(60)
        btn_p2.setStyleSheet("""
            QPushButton { background-color: #16213e; color: white; border: 2px solid #00d9ff; border-radius: 10px; font-size: 20px; min-width: 140px; min-height: 50px; }
            QPushButton:hover { background-color: #00d9ff; color: #1a1a2e; }
        """)
        btn_p2.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_p2)

        wrapper = QWidget()
        wrapper.setLayout(btn_layout)
        wrapper.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(wrapper, 0, Qt.AlignmentFlag.AlignCenter)

        result = dialog.exec()
        self.server = 1 if result == QDialog.DialogCode.Accepted else 2
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
        # Satz-Ergebnis festhalten (vor dem Reset)
        self.set_scores.append((self.score1, self.score2))

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
                # ABBRECHEN: Satz-Ergebnis rückgängig + letzten Punkt zurücknehmen
                if self.set_scores:
                    self.set_scores.pop()
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
            # ERST JETZT in DB speichern (inkl. Einzel-Satz-Ergebnisse)
            if self.main_window and self.main_window.db:
                self.main_window.db.save_match_with_names(
                    self.player1_name, self.player2_name,
                    self.sets1, self.sets2,
                    self.turnier_id,
                    set_scores=self.set_scores
                )

            if self.main_window:
                if self.turnier_id and self.main_window.current_turnier_name:
                    self.main_window.show_turnier_detail(self.turnier_id, self.main_window.current_turnier_name)
                else:
                    self.main_window.show_start_menu()
        else:
            # ABBRECHEN: Satz-Ergebnis und letzten Punkt rückgängig machen
            if self.set_scores:
                self.set_scores.pop()
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
        self.page_keyboard = FullscreenKeyboardPage(self)      # Vollbild-Tastatur
        self.page_neu_turnier = NeuTurnierPage(self)           # Vollbild-Turniererstellung
        self.page_turnier_match = TurnierMatchSetupPage(self)  # Spielerauswahl Turnier

        self.stack.addWidget(self.page_start)          # 0
        self.stack.addWidget(self.page_setup)          # 1
        self.stack.addWidget(self.page_turnier_list)   # 2
        self.stack.addWidget(self.page_turnier_detail) # 3
        self.stack.addWidget(self.page_scoreboard)     # 4
        self.stack.addWidget(self.page_keyboard)       # 5
        self.stack.addWidget(self.page_neu_turnier)    # 6
        self.stack.addWidget(self.page_turnier_match)  # 7

        self.stack.setCurrentIndex(0)
    
    def show_keyboard_for_field(self, target_field, return_index, title="Eingabe", show_suggestions=True):
        """Öffnet Vollbild-Tastatur für ein Eingabefeld."""
        def on_keyboard_close():
            self.stack.setCurrentIndex(return_index)

        self.page_keyboard.open_for_field(target_field, on_keyboard_close, title, show_suggestions=show_suggestions)
        self.stack.setCurrentIndex(5)

    def show_neu_turnier_page(self, return_index, on_created_callback=None):
        """Öffnet die Vollbild-Turniererstellungsseite."""
        self.page_neu_turnier.open(return_index, on_created_callback)
        self.stack.setCurrentIndex(6)
    
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
        self.page_scoreboard.setFocus()
    
    def start_turnier_match(self, turnier_id, turnier_name):
        self.current_turnier_id = turnier_id
        self.current_turnier_name = turnier_name
        self.page_turnier_match.load(turnier_id, turnier_name)
        self.stack.setCurrentIndex(7)  # TurnierMatchSetupPage
    
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