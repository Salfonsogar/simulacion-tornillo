"""
Ventana Principal.

Aplicación con 3 pestañas:
- Calculadora
- Simulación
- Criptografía
"""

import sys

from PyQt6.QtWidgets import QMainWindow, QTabWidget, QApplication, QStatusBar
from PyQt6.QtCore import QSize

from .calculator_tab import CalculatorTab
from .crypto_tab import CryptoTab
from .simulation import SimulationTab


class MainWindow(QMainWindow):
    """
    Ventana principal con QTabWidget.
    
    Pestañas:
    1. Calculadora - Cálculo de VM
    2. Simulación - Animación QPainter + Gráfica matplotlib
    3. Criptografía - Cifrado/descifrado
    """
    
    # Paleta de colores - Tema Claro
    COLORS = {
        'primary': '#0078D4',      # Azul principal
        'primary_dark': '#005A9E',
        'secondary': '#FF6B00',   # Naranja
        'success': '#28A745',      # Verde
        'info': '#17A2B8',         # Cyan
        'warning': '#FF6B00',      # Naranja
        'danger': '#DC3545',      # Rojo
        'light': '#F8F9FA',        # Fondo claro
        'dark': '#212529',        # Texto oscuro
        'border': '#DEE2E6',      # Bordes
        'bg_main': '#FFFFFF',      # Fondo principal
        'bg_secondary': '#F8F9FA', # Fondo secundario
        'text': '#212529',        # Texto
        'text_secondary': '#6C757D', # Texto secundario
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
            QMainWindow {{
                background-color: {c['bg_main']};
            }}
            QWidget {{
                background-color: {c['bg_main']};
                color: {c['text']};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }}
            QTabWidget::pane {{
                border: 1px solid {c['border']};
                background-color: {c['bg_main']};
            }}
            QTabBar {{
                background-color: {c['bg_secondary']};
            }}
            QTabBar::tab {{
                background-color: {c['bg_secondary']};
                color: {c['text_secondary']};
                padding: 10px 20px;
                border: 1px solid {c['border']};
                border-bottom: none;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {c['bg_main']};
                color: {c['primary']};
                font-weight: bold;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {c['light']};
            }}
            QStatusBar {{
                background-color: {c['bg_secondary']};
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
                background-color: {c['primary_dark']};
            }}
            QPushButton:pressed {{
                background-color: {c['primary_dark']};
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
                background: {c['light']};
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
                background-color: {c['light']};
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
        tabs.addTab(self._tab_calc, "Calculadora")
        
        self._tab_sim = SimulationTab()
        tabs.addTab(self._tab_sim, "Simulación")
        
        self._tab_crypto = CryptoTab()
        tabs.addTab(self._tab_crypto, "Criptografía")
        
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