"""
Custom Dialog Functions
========================

Frameless, styled dialog boxes for TTR application.
"""

from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent


def show_custom_confirm_dialog(
    parent: Optional[QWidget],
    title: str,
    text: str
) -> bool:
    """Show a frameless confirmation dialog.
    
    Args:
        parent: Parent widget
        title: Dialog title (not used, kept for compatibility)
        text: Message text to display
    
    Returns:
        True if "Ja" (Yes) was clicked, False if "Nein" (No) was clicked
    
    Example:
        >>> if show_custom_confirm_dialog(self, "Beenden", "Wirklich beenden?"):
        ...     app.quit()
    """
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

    # Layout
    layout = QVBoxLayout(dialog)
    layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
    layout.setSpacing(20)
    layout.setContentsMargins(30, 30, 30, 40)

    # Dialog style
    dialog.setStyleSheet("""
        QDialog {
            background-color: #1a1a2e;
            border: 3px solid #00d9ff;
            border-radius: 15px;
        }
    """)

    # Text label
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

    # Button layout
    btn_layout = QHBoxLayout()
    btn_layout.setSpacing(20)
    btn_layout.setContentsMargins(10, 10, 10, 10)

    # No button (red, left)
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

    # Yes button (blue, right)
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

    # Center buttons
    wrapper = QWidget()
    wrapper.setLayout(btn_layout)
    wrapper.setStyleSheet("background: transparent; border: none;")
    layout.addWidget(wrapper, 0, Qt.AlignmentFlag.AlignCenter)

    return dialog.exec() == QDialog.DialogCode.Accepted


def show_custom_info_dialog(
    parent: Optional[QWidget],
    title: str,
    text: str,
    cancel_text: Optional[str] = None
) -> bool:
    """Show a frameless info dialog with OK button.
    
    Args:
        parent: Parent widget
        title: Dialog title (not used, kept for compatibility)
        text: Message text to display
        cancel_text: Optional cancel button text. If provided, dialog has Cancel button.
    
    Returns:
        True if OK was clicked, False if Cancel was clicked
    
    Example:
        >>> show_custom_info_dialog(self, "Info", "Match gespeichert!")
        >>> # With cancel button:
        >>> if show_custom_info_dialog(self, "Satz", "Satz gewonnen!", cancel_text="Zurück"):
        ...     continue_match()
    """
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

    # Layout
    layout = QVBoxLayout(dialog)
    layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
    layout.setSpacing(20)
    layout.setContentsMargins(30, 30, 30, 40)

    # Dialog style
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
    
    # Text label
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
    
    # Button layout
    btn_layout = QHBoxLayout()
    btn_layout.setSpacing(20)
    btn_layout.setContentsMargins(10, 10, 10, 10)
    
    # Optional cancel button (red, left)
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

    # OK button (blue, right)
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

    # Center buttons
    wrapper = QWidget()
    wrapper.setLayout(btn_layout)
    wrapper.setStyleSheet("background: transparent; border: none;")
    layout.addWidget(wrapper, 0, Qt.AlignmentFlag.AlignCenter)
    
    return dialog.exec() == QDialog.DialogCode.Accepted
