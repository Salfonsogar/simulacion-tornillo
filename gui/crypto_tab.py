"""
Pestaña de Criptografía.

Analogía entre movimiento del tornillo y transformación de datos.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox,
    QTextEdit, QSlider
)
from PyQt6.QtCore import Qt

from controller import CryptoController


class CryptoTab(QWidget):
    """Pestaña de criptografía."""
    
    COLORS = {
        'primary': '#FF6B00',
        'primary_dark': '#E65100',
        'secondary': '#0078D4',
        'success': '#28A745',
        'info': '#17A2B8',
        'danger': '#DC3545',
        'text': '#212529',
        'text_secondary': '#6C757D',
        'border': '#DEE2E6',
        'bg': '#FFFFFF',
        'bg_secondary': '#F8F9FA',
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._controller = CryptoController()
        self._ultimo_cifrado = ""
        self._setup_ui()
    
    def _setup_ui(self):
        c = self.COLORS
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        titulo = QLabel("Criptografia del Tornillo")
        titulo.setStyleSheet(f"color: {c['primary']}; font-size: 18px; font-weight: bold;")
        layout.addWidget(titulo)
        
        desc = QLabel(
            "El giro del tornillo transforma datos.\n"
            "Usa la misma (r, L) para cifrar y descifrar."
        )
        desc.setStyleSheet(f"color: {c['text_secondary']}; font-size: 12px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        grupo = QGroupBox("Parametros (Clave)")
        g_layout = QGridLayout()
        g_layout.setSpacing(12)
        
        g_layout.addWidget(QLabel("Radio (r):"), 0, 0)
        self._input_radio = QLineEdit()
        self._input_radio.setPlaceholderText("0.05")
        self._input_radio.setMaximumWidth(100)
        self._input_radio.setText("0.05")
        g_layout.addWidget(self._input_radio, 0, 1)
        g_layout.addWidget(QLabel("m"), 0, 2)
        
        g_layout.addWidget(QLabel("Paso (L):"), 1, 0)
        self._input_paso = QLineEdit()
        self._input_paso.setPlaceholderText("0.002")
        self._input_paso.setMaximumWidth(100)
        self._input_paso.setText("0.002")
        g_layout.addWidget(self._input_paso, 1, 1)
        g_layout.addWidget(QLabel("m"), 1, 2)
        
        g_layout.addWidget(QLabel("Giros:"), 2, 0)
        self._slider_giros = QSlider(Qt.Orientation.Horizontal)
        self._slider_giros.setMinimum(1)
        self._slider_giros.setMaximum(10)
        self._slider_giros.setValue(1)
        g_layout.addWidget(self._slider_giros, 2, 1)
        self._lbl_giros = QLabel("1")
        self._lbl_giros.setStyleSheet(f"font-weight: bold; color: {c['primary']};")
        g_layout.addWidget(self._lbl_giros, 2, 2)
        
        self._slider_giros.valueChanged.connect(
            lambda v: self._lbl_giros.setText(str(v))
        )
        
        grupo.setLayout(g_layout)
        layout.addWidget(grupo)
        
        g_input = QGroupBox("Entrada")
        g_input_layout = QVBoxLayout()
        self._txt_input = QTextEdit()
        self._txt_input.setPlaceholderText("Escribe texto aqui...")
        self._txt_input.setMaximumHeight(60)
        self._txt_input.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {c['border']};
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }}
        """)
        g_input_layout.addWidget(self._txt_input)
        g_input.setLayout(g_input_layout)
        layout.addWidget(g_input)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self._btn_cifrar = QPushButton(">>> Cifrar")
        self._btn_cifrar.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['success']};
                color: white;
                border: none;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: #218838;
            }}
        """)
        self._btn_cifrar.clicked.connect(self._on_cifrar)
        btn_layout.addWidget(self._btn_cifrar)
        
        self._btn_descifrar = QPushButton("<<< Descifrar")
        self._btn_descifrar.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['info']};
                color: white;
                border: none;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: #138496;
            }}
        """)
        self._btn_descifrar.clicked.connect(self._on_descifrar)
        btn_layout.addWidget(self._btn_descifrar)
        
        layout.addLayout(btn_layout)
        
        g_output = QGroupBox("Salida")
        g_output_layout = QVBoxLayout()
        self._txt_output = QTextEdit()
        self._txt_output.setReadOnly(True)
        self._txt_output.setMaximumHeight(60)
        self._txt_output.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {c['border']};
                border-radius: 4px;
                padding: 8px;
                background-color: {c['bg_secondary']};
                font-family: Consolas, monospace;
            }}
        """)
        g_output_layout.addWidget(self._txt_output)
        
        btn_auto = QPushButton("Copiar al entrada >>>")
        btn_auto.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['secondary']};
                color: white;
                border: none;
                padding: 6px 12px;
                font-size: 11px;
                border-radius: 4px;
            }}
        """)
        btn_auto.clicked.connect(self._copiar_a_entrada)
        g_output_layout.addWidget(btn_auto)
        
        g_output.setLayout(g_output_layout)
        layout.addWidget(g_output)
        
        self._lbl_estado = QLabel("")
        self._lbl_estado.setStyleSheet(f"font-weight: bold; padding: 8px; text-align: center;")
        self._lbl_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._lbl_estado)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _on_cifrar(self):
        try:
            radio = float(self._input_radio.text() or "0.05")
            paso = float(self._input_paso.text() or "0.002")
            num_giros = self._slider_giros.value()
            
            texto = self._txt_input.toPlainText().strip()
            if not texto:
                texto = "HELLO"
            
            texto_cifrado, rondas = self._controller.cifrar_texto(texto, radio, paso, num_giros)
            self._ultimo_cifrado = texto_cifrado
            
            self._txt_output.setPlainText(texto_cifrado)
            self._lbl_estado.setText(f"Cifrado: {texto} -> {texto_cifrado} ({rondas} rondas)")
            self._lbl_estado.setStyleSheet(f"color: #28A745; font-weight: bold; text-align: center;")
            
        except Exception as e:
            self._lbl_estado.setText(f"Error: {str(e)}")
            self._lbl_estado.setStyleSheet(f"color: #DC3545; font-weight: bold;")
    
    def _on_descifrar(self):
        try:
            radio = float(self._input_radio.text() or "0.05")
            paso = float(self._input_paso.text() or "0.002")
            num_giros = self._slider_giros.value()
            
            texto = self._txt_input.toPlainText().strip()
            if not texto:
                if self._ultimo_cifrado:
                    texto = self._ultimo_cifrado
                else:
                    self._lbl_estado.setText("Error: Ingrese texto cifrado")
                    self._lbl_estado.setStyleSheet(f"color: #DC3545; font-weight: bold;")
                    return
            
            for parte in texto.split():
                try:
                    int(parte, 16)
                except ValueError:
                    self._lbl_estado.setText(f"Error: '{texto}' no es formato hexadecimal.\nEj: 6A 67 6E 6E 71")
                    self._lbl_estado.setStyleSheet(f"color: #DC3545; font-weight: bold;")
                    return
            
            resultado = self._controller.descifrar_texto(texto, radio, paso, num_giros)
            self._txt_output.setPlainText(resultado)
            self._lbl_estado.setText(f"Descifrado: {texto} -> {resultado}")
            self._lbl_estado.setStyleSheet(f"color: #17A2B8; font-weight: bold;")
            
        except Exception as e:
            self._lbl_estado.setText(f"Error: {str(e)}")
            self._lbl_estado.setStyleSheet(f"color: #DC3545; font-weight: bold;")
    
    def _copiar_a_entrada(self):
        output = self._txt_output.toPlainText().strip()
        if output:
            self._txt_input.setPlainText(output)
            self._lbl_estado.setText("Copiado! Ahora puede descifrar.")
            self._lbl_estado.setStyleSheet(f"color: {self.COLORS['secondary']}; font-weight: bold;")