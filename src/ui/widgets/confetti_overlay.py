"""
Confetti Overlay Widget
=======================

Animated confetti explosion effect for celebrating set/match wins.
"""

import random
import math
from typing import List, Optional

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QBrush

from ...core.constants import CONFETTI_PARTICLE_COUNT, CONFETTI_FPS


class ConfettiParticle:
    """Single confetti particle with physics simulation.
    
    Attributes:
        x, y: Position
        size: Particle size in pixels
        speed_x, speed_y: Velocity components
        gravity: Gravitational acceleration
        friction: Air resistance coefficient
        rotation: Current rotation angle
        rotation_speed: Rotation velocity
        life: Remaining lifetime (1.0 = full, 0.0 = dead)
        fade_speed: How fast the particle fades out
        color: QColor of the particle
    """
    
    def __init__(self, x: float, y: float, color: QColor, angle: float) -> None:
        """Initialize a confetti particle.
        
        Args:
            x: Initial x position
            y: Initial y position
            color: Particle color
            angle: Launch angle in degrees (0-360)
        """
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(15, 30)
        
        # Calculate velocity from angle (explosion effect)
        speed = random.uniform(25, 75)
        self.speed_x = math.cos(math.radians(angle)) * speed
        self.speed_y = math.sin(math.radians(angle)) * speed
        
        # Physics parameters
        self.gravity = 0.30  # Lighter for longer flight time
        self.friction = 0.96  # Air resistance
        
        # Rotation
        self.rotation = random.randint(0, 360)
        self.rotation_speed = random.uniform(-15, 15)
        
        # Lifetime
        self.life = 1.0
        self.fade_speed = random.uniform(0.002, 0.006)


class ConfettiOverlay(QWidget):
    """Transparent overlay widget that displays confetti explosion animation.
    
    Used to celebrate set or match wins. The confetti explodes from the
    center of the widget in all directions with physics simulation.
    
    Example:
        >>> confetti = ConfettiOverlay(parent_widget)
        >>> confetti.start_confetti()  # Start animation
        >>> # Click anywhere to stop, or call:
        >>> confetti.stop_confetti()
    """
    
    # Festive color palette
    CONFETTI_COLORS = [
        QColor("#FFD700"),  # Gold
        QColor("#FF6B6B"),  # Red
        QColor("#4ECDC4"),  # Turquoise
        QColor("#45B7D1"),  # Light Blue
        QColor("#96E6A1"),  # Light Green
        QColor("#DDA0DD"),  # Purple
        QColor("#FF8C42"),  # Orange
        QColor("#00d9ff"),  # Cyan (matches theme)
        QColor("#FFFFFF"),  # White
    ]
    
    def __init__(self, parent: Optional[QWidget] = None, side: str = "left") -> None:
        """Initialize confetti overlay.
        
        Args:
            parent: Parent widget
            side: "left" or "right" (for future use, currently unused)
        """
        super().__init__(parent)
        
        self.side = side
        self.particles: List[ConfettiParticle] = []
        self.is_active = False
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_particles)
        
        # Transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")
    
    def start_confetti(self) -> None:
        """Start the confetti explosion animation."""
        self.is_active = True
        self.particles = []
        
        # Match parent size
        if self.parent():
            self.resize(self.parent().size())
        
        # Explosion from center
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # Create particles in all directions (360°)
        for _ in range(CONFETTI_PARTICLE_COUNT):
            angle = random.uniform(0, 360)
            color = random.choice(self.CONFETTI_COLORS)
            self.particles.append(ConfettiParticle(center_x, center_y, color, angle))
        
        self.show()
        self.raise_()
        self.timer.start(1000 // CONFETTI_FPS)  # Timer interval in ms
    
    def stop_confetti(self) -> None:
        """Stop the confetti animation and hide overlay."""
        self.is_active = False
        self.timer.stop()
        self.particles = []
        self.hide()
    
    def _update_particles(self) -> None:
        """Update particle physics (called by timer)."""
        if not self.is_active:
            return
        
        # Update each particle
        for p in self.particles:
            # Apply velocity
            p.x += p.speed_x
            p.y += p.speed_y
            
            # Apply gravity
            p.speed_y += p.gravity
            
            # Apply air resistance
            p.speed_x *= p.friction
            p.speed_y *= p.friction
            
            # Update rotation
            p.rotation += p.rotation_speed
            
            # Fade out
            p.life -= p.fade_speed
        
        # Remove dead particles
        self.particles = [p for p in self.particles if p.life > 0]
        
        # Stop if all particles are gone
        if not self.particles:
            self.stop_confetti()
        
        self.update()  # Trigger repaint
    
    def paintEvent(self, event) -> None:
        """Paint the confetti particles."""
        if not self.is_active or not self.particles:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        for p in self.particles:
            painter.save()
            
            # Transform to particle position and rotation
            painter.translate(p.x, p.y)
            painter.rotate(p.rotation)
            
            # Set color with alpha based on lifetime
            color = QColor(p.color)
            color.setAlphaF(p.life)
            
            brush = QBrush(color)
            painter.setBrush(brush)
            painter.setPen(Qt.PenStyle.NoPen)
            
            # Draw rectangular confetti
            painter.drawRect(
                int(-p.size / 2),
                int(-p.size / 4),
                p.size,
                int(p.size / 2)
            )
            
            painter.restore()
    
    def mousePressEvent(self, event) -> None:
        """Stop animation on click."""
        self.stop_confetti()
        event.accept()
