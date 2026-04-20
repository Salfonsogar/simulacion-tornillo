"""
Ventana Principal.

Aplicación con 4 pestañas:
- Calculadora
- Simulación
- Criptografía
- Reto Diseño (Metodología Inversa)
"""

import sys

from PyQt6.QtWidgets import QMainWindow, QTabWidget, QApplication, QStatusBar
from PyQt6.QtCore import QSize

from .calculator_tab import CalculatorTab
from .crypto_tab import CryptoTab
from .simulation.simulation_tab import SimulationTab
from .inverse_tab import InverseTab


class MainWindow(QMainWindow):
    """
    Ventana principal con QTabWidget.
    
    Pestañas:
    1. Calculadora - Cálculo de VM
    2. Simulación - Animación QPainter + Gráfica matplotlib
    3. Criptografía - Cifrado/descifrado
    """
    
    # Paleta de colores unificada - Tema Profesional (Modern Blue & Orange)
    COLORS = {
        'primary': '#0078D4',        # Azul corporativo
        'primary_hover': '#005A9E',
        'accent': '#FF6B00',         # Naranja para acciones
        'accent_hover': '#E65100',
        'success': '#107C10',        # Verde éxito
        'info': '#0078D4',           # Informativo
        'danger': '#A4262C',         # Rojo error
        'bg_main': '#F3F2F1',        # Gris muy claro fondo
        'bg_card': '#FFFFFF',        # Blanco para contenedores
        'border': '#EDEBE9',         # Borde sutil
        'text': '#201F1E',           # Texto principal
        'text_secondary': '#605E5C', # Texto secundario/desactivado
        'selection': '#CCE4F6',      # Azul selección
    }
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Simulador de Tornillo con Sistema Dinámico")
        self.setMinimumSize(900, 700)
        self.resize(1100, 800)
        
        self._aplicar_estilo()
        self._setup_ui()
        self._setup_estado()
    
    def _aplicar_estilo(self):
        c = self.COLORS
        
        estilo = f"""
            QMainWindow, QWidget {{
                background-color: {c['bg_main']};
                color: {c['text']};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }}
            QTabWidget::pane {{
                border: 1px solid {c['border']};
                background-color: {c['bg_card']};
                border-radius: 4px;
            }}
            QTabBar {{
                background-color: transparent;
            }}
            QTabBar::tab {{
                background-color: {c['bg_main']};
                color: {c['text_secondary']};
                padding: 12px 25px;
                border: 1px solid {c['border']};
                border-bottom: none;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            QTabBar::tab:selected {{
                background-color: {c['bg_card']};
                color: {c['primary']};
                font-weight: bold;
                border-bottom: 2px solid {c['primary']};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {c['selection']};
            }}
            QStatusBar {{
                background-color: {c['bg_card']};
                color: {c['text_secondary']};
                border-top: 1px solid {c['border']};
            }}
            QGroupBox {{
                border: 1px solid {c['border']};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: {c['text']};
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                color: {c['primary']};
            }}
            QPushButton {{
                background-color: {c['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {c['primary_hover']};
            }}
            QPushButton:pressed {{
                background-color: {c['primary_hover']};
            }}
            QLineEdit, QTextEdit {{
                background-color: white;
                border: 1px solid {c['border']};
                border-radius: 4px;
                padding: 6px 8px;
                color: {c['text']};
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 2px solid {c['primary']};
            }}
            QLabel {{
                color: {c['text']};
                background-color: transparent;
            }}
            QSlider::groove:horizontal {{
                background: {c['bg_main']};
                height: 8px;
                border-radius: 4px;
                border: 1px solid {c['border']};
            }}
            QSlider::handle:horizontal {{
                background: {c['primary']};
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
            QProgressBar {{
                border: 1px solid {c['border']};
                border-radius: 4px;
                text-align: center;
                background-color: {c['bg_main']};
            }}
            QProgressBar::chunk {{
                background-color: {c['primary']};
                border-radius: 3px;
            }}
        """
        self.setStyleSheet(estilo)
    
    def _setup_ui(self):
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        
        self._tab_calc = CalculatorTab()
        tabs.addTab(self._tab_calc, "📊 Calculadora")
        
        self._tab_sim = SimulationTab()
        tabs.addTab(self._tab_sim, "🎬 Simulación")
        
        self._tab_crypto = CryptoTab()
        tabs.addTab(self._tab_crypto, "🔐 Criptografía")
        
        self._tab_inverse = InverseTab()
        tabs.addTab(self._tab_inverse, "🔧 Reto Diseño")
        
        self.setCentralWidget(tabs)
        
        from PyQt6.QtCore import QSize
        tabs.setIconSize(QSize(20, 20))
    
    def _setup_estado(self):
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.showMessage("Listo")


def ejecutar():
    """Función para ejecutar la aplicación."""
    app = QApplication(sys.argv)
    app.setApplicationName("Simulador de Tornillo")
    app.setApplicationVersion("1.0.0")
    
    ventana = MainWindow()
    ventana.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    ejecutar()