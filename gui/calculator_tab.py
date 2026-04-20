"""
Pestaña de Calculadora.

Calcula la Ventaja Mecánica (VM) del tornillo:
- VM = (2πr) / L
- F_salida = F_entrada × VM
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox
)
from PyQt6.QtCore import Qt

from controller import CalculatorController


class CalculatorTab(QWidget):
    """Pestaña calculadora del tornillo."""
    
    COLORS = {
        'primary': '#0078D4',
        'primary_dark': '#005A9E',
        'success': '#28A745',
        'text': '#212529',
        'text_secondary': '#6C757D',
        'border': '#DEE2E6',
        'bg': '#FFFFFF',
        'bg_secondary': '#F8F9FA',
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._controller = CalculatorController()
        self._setup_ui()
    
    def _setup_ui(self):
        c = self.COLORS
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        titulo = QLabel("Calculadora del Tornillo")
        titulo.setStyleSheet(f"color: {c['primary']}; font-size: 18px; font-weight: bold;")
        layout.addWidget(titulo)
        
        desc = QLabel(
            "Calcula la Ventaja Mecanica (VM) del tornillo como maquina simple.\n"
            "Formula: VM = (2*pi*r) / L"
        )
        desc.setStyleSheet(f"color: {c['text_secondary']}; font-size: 12px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        grupo = QGroupBox("Parametros de Entrada")
        g_layout = QGridLayout()
        g_layout.setSpacing(12)
        
        g_layout.addWidget(QLabel("Masa (m):"), 0, 0)
        self._input_masa = QLineEdit()
        self._input_masa.setPlaceholderText("1.0")
        self._input_masa.setMaximumWidth(100)
        g_layout.addWidget(self._input_masa, 0, 1)
        g_layout.addWidget(QLabel("kg"), 0, 2)
        
        g_layout.addWidget(QLabel("Radio (r):"), 1, 0)
        self._input_radio = QLineEdit()
        self._input_radio.setPlaceholderText("0.05")
        self._input_radio.setMaximumWidth(100)
        g_layout.addWidget(self._input_radio, 1, 1)
        g_layout.addWidget(QLabel("m"), 1, 2)
        
        g_layout.addWidget(QLabel("Paso (L):"), 2, 0)
        self._input_paso = QLineEdit()
        self._input_paso.setPlaceholderText("0.002")
        self._input_paso.setMaximumWidth(100)
        g_layout.addWidget(self._input_paso, 2, 1)
        g_layout.addWidget(QLabel("m"), 2, 2)
        
        grupo.setLayout(g_layout)
        layout.addWidget(grupo)
        
        self._btn_calcular = QPushButton("Calcular VM")
        self._btn_calcular.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['primary']};
                color: white;
                border: none;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {c['primary_dark']};
            }}
        """)
        self._btn_calcular.clicked.connect(self._calcular)
        layout.addWidget(self._btn_calcular)
        
        self._resultado = QLabel("VM: --")
        self._resultado.setStyleSheet(f"""
            color: {c['primary']};
            font-size: 28px;
            font-weight: bold;
            padding: 20px;
            background-color: {c['bg_secondary']};
            border-radius: 8px;
            border: 1px solid {c['border']};
        """)
        self._resultado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._resultado)
        
        self._info = QLabel("")
        self._info.setStyleSheet(f"color: {c['text_secondary']}; font-size: 12px;")
        self._info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._info)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _calcular(self):
        try:
            radio = float(self._input_radio.text() or "0.05")
            paso = float(self._input_paso.text() or "0.002")
            
            vm = self._controller.calcular_vm(radio, paso)
            
            self._resultado.setText(f"VM: {vm:.4f}")
            self._info.setText(
                f"r = {radio}m, L = {paso}m\n"
                f"Con VM = {vm:.2f}x, una fuerza de 1N se convierte en {vm:.2f}N"
            )
        except Exception as e:
            self._resultado.setText("Error")
            self._info.setText(str(e))