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
