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
        'primary_hover': '#005A9E',
        'accent': '#FF6B00',
        'success': '#107C10',
        'text': '#201F1E',
        'text_secondary': '#605E5C',
        'border': '#EDEBE9',
        'bg_card': '#FFFFFF',
        'bg_main': '#F3F2F1',
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._controller = CalculatorController()
        self._setup_ui()
    
    def _setup_ui(self):
        c = self.COLORS
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        titulo = QLabel("📊 Calculadora de Ventaja Mecánica")
        titulo.setStyleSheet(f"color: {c['primary']}; font-size: 22px; font-weight: bold;")
        layout.addWidget(titulo)
        
        desc = QLabel(
            "Determine la fuerza de salida y la ventaja mecánica teórica del tornillo "
            "basado en sus dimensiones geométricas."
        )
        desc.setStyleSheet(f"color: {c['text_secondary']}; font-size: 13px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        grupo = QGroupBox("Parámetros del Sistema")
        grupo.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid {c['border']};
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 20px;
                background-color: {c['bg_card']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                padding: 0 10px;
                color: {c['primary']};
            }}
        """)
        g_layout = QGridLayout()
        g_layout.setSpacing(15)
        
        def create_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color: {c['text']}; font-weight: 500;")
            return lbl
        
        g_layout.addWidget(create_label("Radio (r):"), 1, 0)
        self._input_radio = QLineEdit("0.05")
        self._input_radio.setMinimumHeight(35)
        self._input_radio.setStyleSheet(f"border: 1px solid {c['border']}; border-radius: 4px; padding: 5px;")
        g_layout.addWidget(self._input_radio, 1, 1)
        g_layout.addWidget(QLabel("m"), 1, 2)
        
        g_layout.addWidget(create_label("Paso (L):"), 2, 0)
        self._input_paso = QLineEdit("0.002")
        self._input_paso.setMinimumHeight(35)
        self._input_paso.setStyleSheet(f"border: 1px solid {c['border']}; border-radius: 4px; padding: 5px;")
        g_layout.addWidget(self._input_paso, 2, 1)
        g_layout.addWidget(QLabel("m"), 2, 2)
        
        grupo.setLayout(g_layout)
        layout.addWidget(grupo)
        
        self._btn_calcular = QPushButton("Calcular Análisis")
        self._btn_calcular.setMinimumHeight(45)
        self._btn_calcular.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_calcular.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['primary']};
                color: white;
                border: none;
                padding: 10px 25px;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {c['primary_hover']};
            }}
        """)
        self._btn_calcular.clicked.connect(self._calcular)
        layout.addWidget(self._btn_calcular)
        
        res_container = QWidget()
        res_container.setStyleSheet(f"background-color: {c['bg_main']}; border-radius: 10px; border: 1px solid {c['border']};")
        res_layout = QVBoxLayout(res_container)
        
        self._resultado = QLabel("VM: --")
        self._resultado.setStyleSheet(f"color: {c['primary']}; font-size: 32px; font-weight: bold; border: none; background: transparent;")
        self._resultado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        res_layout.addWidget(self._resultado)
        
        self._info = QLabel("Ingrese los datos para iniciar el cálculo")
        self._info.setStyleSheet(f"color: {c['text_secondary']}; font-size: 13px; border: none; background: transparent;")
        self._info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        res_layout.addWidget(self._info)
        
        layout.addWidget(res_container)
        
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